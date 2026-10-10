// =============================================================================
// ALUR SISTEM: PREVIEW & EDIT SCREEN (VERIFIKASI & KOREKSI DATA PENGGUNA)
// =============================================================================
// Peran dalam Arsitektur:
// 1. INPUT:
//    - Objek Transaction (bisa dari hasil ekstraksi otomatis OfflineReceiptService
//      atau transaksi baru kosongan jika memilih "Catat Manual")
// 2. LOGIKA KONTROL & FORMATTING FORM:
//    - CurrencyTextInputFormatter: Live formatting pemisah ribuan titik (contoh: 18.000)
//    - Subtotal per item: Qty x Harga Satuan dihitung otomatis
//    - Auto-Sync Total: Nilai Total Belanja otomatis disinkronkan dengan Σ(Subtotal item)
//      namun tetap dapat dikoreksi manual jika kasir memberikan diskon global
//    - PopScope: Menahan tombol kembali untuk mencegah data hilang tanpa konfirmasi
// 3. PERSISTENSI KE DATABASE:
//    - Tombol "Simpan Transaksi" -> _saveTransaction()
//    - Memanggil DatabaseHelper.instance.insertTransaction(trx, items)
// 4. OUTPUT:
//    - Navigator.pop(context, true) -> memberitahu DashboardScreen untuk refresh data
// =============================================================================

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../db/database_helper.dart';
import '../models/transaction.dart';
import '../models/transaction_item.dart';
import '../utils/currency_format_helper.dart';
import 'item_detail_screen.dart';

class _ItemRowController {
  final TextEditingController nameController;
  final TextEditingController qtyController;
  final TextEditingController priceController;

  _ItemRowController({
    required String name,
    required int qty,
    required double price,
  })  : nameController = TextEditingController(text: name),
        qtyController = TextEditingController(text: qty.toString()),
        priceController = TextEditingController(text: CurrencyFormatHelper.formatReceipt(price));

  void dispose() {
    nameController.dispose();
    qtyController.dispose();
    priceController.dispose();
  }
}

/// Halaman Pratinjau & Edit Transaksi (BAB 4.2 poin 2): menampilkan hasil
/// ekstraksi On-Device (nama toko, daftar barang, harga, total) dan
/// memungkinkan pengguna mengoreksi sebelum disimpan ke SQLite.
class PreviewEditScreen extends StatefulWidget {
  const PreviewEditScreen({
    super.key,
    required this.transaction,
    this.executionTimeMs,
    this.modelName,
    this.isDateEstimated = false,
  });

  final Transaction transaction;
  final int? executionTimeMs;
  final String? modelName;
  final bool isDateEstimated;

  @override
  State<PreviewEditScreen> createState() => _PreviewEditScreenState();
}

class _PreviewEditScreenState extends State<PreviewEditScreen> {
  late final TextEditingController _storeController;
  late final TextEditingController _totalController;
  late List<TransactionItem> _items;
  final List<_ItemRowController> _itemControllers = [];
  late DateTime _transactionDate;
  late String _selectedCategory;
  bool _isSaving = false;
  double _discount = 0.0;

  static const List<Map<String, dynamic>> _categories = [
    {'name': 'Belanja Harian', 'icon': Icons.shopping_cart_outlined},
    {'name': 'Makanan & Minuman', 'icon': Icons.restaurant_outlined},
    {'name': 'Transportasi', 'icon': Icons.directions_car_outlined},
    {'name': 'Tagihan & Utilitas', 'icon': Icons.receipt_long_outlined},
    {'name': 'Kesehatan', 'icon': Icons.medical_services_outlined},
    {'name': 'Hiburan', 'icon': Icons.movie_outlined},
    {'name': 'Lainnya', 'icon': Icons.category_outlined},
  ];

  @override
  void initState() {
    super.initState();
    _storeController = TextEditingController(text: widget.transaction.storeName);
    _items = List.of(widget.transaction.items);
    for (final it in _items) {
      _itemControllers.add(_ItemRowController(
        name: it.itemName,
        qty: it.quantity,
        price: it.itemPrice,
      ));
    }
    _transactionDate = widget.transaction.transactionDate;
    _selectedCategory = widget.transaction.category.isNotEmpty
        ? widget.transaction.category
        : 'Belanja Harian';
    final double initialItemsSum = _items.fold(0.0, (sum, it) => sum + it.subtotal);
    if (initialItemsSum > widget.transaction.totalAmount && widget.transaction.totalAmount > 0) {
      _discount = initialItemsSum - widget.transaction.totalAmount;
    }
    _totalController = TextEditingController(
      text: CurrencyFormatHelper.formatReceipt(widget.transaction.totalAmount),
    );
  }

  @override
  void dispose() {
    _storeController.dispose();
    _totalController.dispose();
    for (final c in _itemControllers) {
      c.dispose();
    }
    super.dispose();
  }

  double get _total => CurrencyFormatHelper.parsePrice(_totalController.text);

  // Total Harga Barang (Hanya item positif / sebelum diskon)
  double get _grossItemsSum => _items
      .where((it) => it.itemPrice > 0 && !it.itemName.toLowerCase().contains('potongan'))
      .fold(0.0, (sum, it) => sum + it.subtotal);

  // Total Potongan Diskon dari rincian item (nominal absolut positif)
  double get _itemDiscountsSum => _items
      .where((it) => it.itemPrice < 0 || it.itemName.toLowerCase().contains('potongan'))
      .fold(0.0, (sum, it) => sum + it.subtotal.abs());

  // Total Potongan Keseluruhan
  double get _totalDiscountSum => _itemDiscountsSum + _discount;

  // Total Belanja Bersih
  double get _netTotal {
    final net = _grossItemsSum - _totalDiscountSum;
    return net > 0 ? net : 0.0;
  }

  void _recalculateTotal() {
    if (_items.isEmpty) return;
    _totalController.text = CurrencyFormatHelper.formatReceipt(_netTotal);
  }

  Future<void> _pickDateTime() async {
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: _transactionDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      helpText: 'Pilih Tanggal Struk',
    );
    if (pickedDate == null || !mounted) return;

    final pickedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: _transactionDate.hour, minute: _transactionDate.minute),
      helpText: 'Pilih Jam Struk',
    );
    if (!mounted) return;

    setState(() {
      _transactionDate = DateTime(
        pickedDate.year,
        pickedDate.month,
        pickedDate.day,
        pickedTime?.hour ?? _transactionDate.hour,
        pickedTime?.minute ?? _transactionDate.minute,
      );
    });
  }

  void _addItem() {
    setState(() {
      final newItem = TransactionItem(itemName: 'Item baru', itemPrice: 0, quantity: 1);
      _items.add(newItem);
      _itemControllers.add(_ItemRowController(
        name: newItem.itemName,
        qty: newItem.quantity,
        price: newItem.itemPrice,
      ));
      _recalculateTotal();
    });
  }

  void _removeItem(int index) {
    setState(() {
      _items.removeAt(index);
      _itemControllers.removeAt(index).dispose();
      _recalculateTotal();
    });
  }

  Future<bool> _confirmDiscard() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Batalkan Pengisian?'),
        content: const Text(
          'Data hasil ekstraksi struk ini belum disimpan. Apakah Anda yakin ingin membatalkan dan keluar?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Tetap di Sini'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red.shade700,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Ya, Batalkan'),
          ),
        ],
      ),
    );

    if (result == true && widget.transaction.imagePath != null && widget.transaction.id == null) {
      try {
        final tempFile = File(widget.transaction.imagePath!);
        if (await tempFile.exists()) {
          await tempFile.delete();
        }
      } catch (_) {}
    }

    return result ?? false;
  }

  Future<void> _save() async {
    if (_isSaving) return;

    if (_total <= 0 && _items.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Mohon masukkan nominal total atau tambahkan minimal 1 item barang.'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      // Hapus file citra sementara di cache kamera/galeri.
      // Sesuai prinsip efisiensi offline-first, foto fisik struk tidak disimpan permanen
      // karena seluruh entitas transaksi (nama toko, tanggal, rincian barang, total)
      // sudah sukses terekstraksi 100% ke dalam database relasional SQLite.
      if (widget.transaction.imagePath != null && widget.transaction.id == null) {
        try {
          final tempFile = File(widget.transaction.imagePath!);
          if (await tempFile.exists()) {
            await tempFile.delete();
          }
        } catch (_) {}
      }

      final trx = widget.transaction.copyWith(
        storeName: _storeController.text.trim().isEmpty
            ? 'Pengeluaran Manual'
            : _storeController.text.trim(),
        category: _selectedCategory,
        totalAmount: _total,
        transactionDate: _transactionDate,
        imagePath: null, // Bebas bloat: foto tidak disimpan ke storage perangkat
        items: _items,
      );

      if (trx.id != null) {
        await DatabaseHelper.instance.updateTransaction(trx);
        if (!mounted) return;
        Navigator.of(context).pop(true);
      } else {
        final id = await DatabaseHelper.instance.insertTransaction(trx);
        if (!mounted) return;
        await Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => ItemDetailScreen(transactionId: id)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal menyimpan transaksi: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditingExisting = widget.transaction.id != null;
    final isManualInput = widget.transaction.storeName.isEmpty && widget.transaction.id == null;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        final shouldPop = await _confirmDiscard();
        if (shouldPop && context.mounted) {
          Navigator.of(context).pop(false);
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(isEditingExisting
              ? 'Edit Transaksi'
              : (isManualInput ? 'Catat Pengeluaran' : 'Pratinjau & Edit')),
          actions: [
            IconButton(
              onPressed: _isSaving ? null : _save,
              icon: _isSaving
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.check),
              tooltip: isEditingExisting ? 'Simpan Perubahan' : 'Simpan Transaksi',
            ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (widget.executionTimeMs != null) ...[
              Card(
                color: Colors.teal.shade50.withValues(alpha: 0.6),
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: BorderSide(color: Colors.teal.shade200),
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  child: Row(
                    children: [
                      Icon(
                        Icons.bolt_outlined,
                        color: Colors.teal.shade800,
                        size: 24,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.modelName ?? 'On-Device Machine Learning (ML Kit)',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                                color: Colors.teal.shade900,
                              ),
                            ),
                            Text(
                              'Waktu komputasi: ${widget.executionTimeMs} ms (${(widget.executionTimeMs! / 1000).toStringAsFixed(2)} detik) • 100% Offline',
                              style: TextStyle(fontSize: 11, color: Colors.teal.shade700),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            TextField(
              controller: _storeController,
              decoration: const InputDecoration(
                labelText: 'Nama Toko / Merchant',
                prefixIcon: Icon(Icons.storefront_outlined, color: Colors.teal),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),

            // Dropdown Kategori Pengeluaran
            DropdownButtonFormField<String>(
              initialValue: _selectedCategory,
              decoration: const InputDecoration(
                labelText: 'Kategori Pengeluaran',
                prefixIcon: Icon(Icons.label_outline, color: Colors.teal),
                border: OutlineInputBorder(),
              ),
              items: _categories.map((cat) {
                return DropdownMenuItem<String>(
                  value: cat['name'] as String,
                  child: Row(
                    children: [
                      Icon(cat['icon'] as IconData, size: 20, color: Colors.teal.shade700),
                      const SizedBox(width: 10),
                      Text(cat['name'] as String),
                    ],
                  ),
                );
              }).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedCategory = val);
              },
            ),
            const SizedBox(height: 14),

            // Pemilih Tanggal & Waktu Struk
            InkWell(
              onTap: _pickDateTime,
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade400),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.event, color: Colors.teal),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Text(
                                'Tanggal & Waktu Transaksi',
                                style: TextStyle(fontSize: 11, color: Colors.grey),
                              ),
                              if (widget.isDateEstimated) ...[
                                const SizedBox(width: 6),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.teal.shade50,
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(color: Colors.teal.shade300, width: 0.8),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.info_outline, size: 11, color: Colors.teal.shade800),
                                      const SizedBox(width: 3),
                                      Text(
                                        'Diperkirakan',
                                        style: TextStyle(
                                          fontSize: 9.5,
                                          fontWeight: FontWeight.w600,
                                          color: Colors.teal.shade900,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            DateFormat('EEEE, dd MMM yyyy - HH:mm', 'id_ID').format(_transactionDate),
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.edit_calendar, size: 20, color: Colors.teal),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Rincian Barang (${_items.length} item)',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: _addItem,
                  icon: const Icon(Icons.add_circle_outline, size: 18),
                  label: const Text('Tambah'),
                ),
              ],
            ),
            const SizedBox(height: 8),

            ..._items.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              final rowCtrl = _itemControllers[index];
              final isDiscount = item.itemPrice < 0 || item.itemName.toLowerCase().contains('potongan');
              return Card(
                key: ObjectKey(rowCtrl),
                margin: const EdgeInsets.only(bottom: 12),
                elevation: isDiscount ? 0 : 0.5,
                color: isDiscount ? Colors.amber.shade50.withValues(alpha: 0.4) : null,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: BorderSide(
                    color: isDiscount ? Colors.amber.shade300 : Colors.grey.shade300,
                    width: isDiscount ? 1.2 : 1.0,
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Badge untuk baris diskon agar tidak disalahpahami sebagai barang belanjaan biasa
                      if (isDiscount) ...[
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.amber.shade800,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.local_offer_outlined, size: 11, color: Colors.white),
                                  SizedBox(width: 3),
                                  Text(
                                    'POTONGAN / VOUCHER',
                                    style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.white),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                      ],
                      // Baris 1: Nama Barang / Keterangan Potongan (Full Width) & Tombol Hapus
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          Expanded(
                            child: TextFormField(
                              controller: rowCtrl.nameController,
                              decoration: InputDecoration(
                                labelText: isDiscount ? 'Keterangan Potongan / Diskon' : 'Nama Barang / Produk',
                                isDense: true,
                                contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 11),
                                border: const OutlineInputBorder(),
                              ),
                              onChanged: (v) => _items[index] = _items[index].copyWith(itemName: v),
                            ),
                          ),
                          const SizedBox(width: 8),
                          IconButton(
                            onPressed: () => _removeItem(index),
                            icon: const Icon(Icons.delete_outline, color: Colors.redAccent, size: 22),
                            tooltip: 'Hapus Item',
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      // Baris 2: Kuantitas (Qty) & Harga Satuan & Subtotal (Responsif di Layar Kecil)
                      Row(
                        children: [
                          SizedBox(
                            width: 68,
                            child: TextFormField(
                              controller: rowCtrl.qtyController,
                              readOnly: isDiscount,
                              decoration: InputDecoration(
                                labelText: 'Qty',
                                isDense: true,
                                contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 11),
                                border: const OutlineInputBorder(),
                                fillColor: isDiscount ? Colors.grey.shade100 : null,
                                filled: isDiscount,
                              ),
                              keyboardType: TextInputType.number,
                              onChanged: isDiscount
                                  ? null
                                  : (v) {
                                      final q = int.tryParse(v) ?? 1;
                                      setState(() {
                                        _items[index] = _items[index].copyWith(quantity: q);
                                        _recalculateTotal();
                                      });
                                    },
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              controller: rowCtrl.priceController,
                              decoration: InputDecoration(
                                labelText: isDiscount ? 'Nominal Potongan' : 'Harga Satuan',
                                prefixText: isDiscount ? '' : 'Rp ',
                                isDense: true,
                                contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 11),
                                border: const OutlineInputBorder(),
                              ),
                              keyboardType: const TextInputType.numberWithOptions(signed: true),
                              inputFormatters: [CurrencyTextInputFormatter(allowNegative: true)],
                              onChanged: (v) {
                                final parsed = CurrencyFormatHelper.parsePrice(v);
                                setState(() {
                                  _items[index] = _items[index].copyWith(itemPrice: parsed);
                                  _recalculateTotal();
                                });
                              },
                            ),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                isDiscount
                                    ? 'Potongan'
                                    : '${item.quantity} × ${CurrencyFormatHelper.formatReceipt(item.itemPrice)}',
                                style: TextStyle(
                                  fontSize: 10.5,
                                  color: isDiscount ? Colors.amber.shade900 : Colors.grey.shade600,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 1),
                              Text(
                                isDiscount
                                    ? '- ${CurrencyFormatHelper.formatRp(item.subtotal.abs())}'
                                    : CurrencyFormatHelper.formatRp(item.subtotal),
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.bold,
                                  color: isDiscount ? Colors.red.shade700 : Colors.teal.shade800,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            }),

            // Ringkasan Finansial Kasir: Total Harga, Total Discount, dan Total Belanja
            if (_items.isNotEmpty) ...[
              const SizedBox(height: 8),
              Builder(
                builder: (context) {
                  final double gross = _grossItemsSum;
                  final double discount = _totalDiscountSum;
                  final double calculatedNet = _netTotal;
                  final double totalKasir = _total;
                  final double discrepancy = totalKasir - calculatedNet;
                  final int productCount = _items
                      .where((it) => it.itemPrice > 0 && !it.itemName.toLowerCase().contains('potongan'))
                      .length;

                  return Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.teal.shade50.withValues(alpha: 0.6),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.teal.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Baris 1: Total Harga (Sebelum diskon)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Total Harga ($productCount produk):',
                              style: TextStyle(fontSize: 13, color: Colors.grey.shade800),
                            ),
                            Text(
                              CurrencyFormatHelper.formatRp(gross),
                              style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600, color: Colors.grey.shade900),
                            ),
                          ],
                        ),

                        // Baris 2: Total Discount (Jika ada diskon)
                        if (discount > 0.01) ...[
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                    decoration: BoxDecoration(
                                      color: Colors.amber.shade800,
                                      borderRadius: BorderRadius.circular(3),
                                    ),
                                    child: const Text(
                                      'DISKON',
                                      style: TextStyle(fontSize: 8.5, color: Colors.white, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Total Discount:',
                                    style: TextStyle(fontSize: 13, color: Colors.amber.shade900, fontWeight: FontWeight.w600),
                                  ),
                                ],
                              ),
                              Text(
                                '- ${CurrencyFormatHelper.formatRp(discount)}',
                                style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.bold, color: Colors.red.shade700),
                              ),
                            ],
                          ),
                        ],

                        // Baris Selisih jika ada selisih kasir / pembulatan
                        if (discrepancy.abs() > 0.01) ...[
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                discrepancy.abs() <= 500 ? 'Pembulatan Kasir:' : 'Selisih Kasir / Koreksi:',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                              ),
                              Text(
                                '${discrepancy > 0 ? '+' : '-'} ${CurrencyFormatHelper.formatRp(discrepancy.abs())}',
                                style: TextStyle(
                                  fontSize: 12.5,
                                  fontWeight: FontWeight.bold,
                                  color: discrepancy.abs() <= 500 ? Colors.grey.shade800 : Colors.amber.shade900,
                                ),
                              ),
                            ],
                          ),
                          if (discrepancy.abs() > 500) ...[
                            const SizedBox(height: 6),
                            Container(
                              padding: const EdgeInsets.all(7),
                              decoration: BoxDecoration(
                                color: Colors.amber.shade50,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.amber.shade300),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(Icons.info_outline, size: 14, color: Colors.amber.shade900),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      'Terdapat selisih ${CurrencyFormatHelper.formatRp(discrepancy.abs())} antara total kasir dan rincian item. Silakan periksa apakah ada barang yang terpotong nominalnya saat scan.',
                                      style: TextStyle(fontSize: 10.5, color: Colors.brown.shade900),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],

                        const Divider(height: 20),

                        // Baris 3: Total Belanja (Total Akhir Kasir)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Total Belanja:',
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              CurrencyFormatHelper.formatRp(totalKasir),
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.teal.shade900,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],

            const Divider(height: 28),

            TextField(
              controller: _totalController,
              readOnly: true,
              enableInteractiveSelection: false,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.teal.shade900,
                  ),
              decoration: InputDecoration(
                labelText: 'Total Belanja (Dihitung Otomatis)',
                prefixText: 'Rp ',
                filled: true,
                fillColor: Colors.teal.shade50.withValues(alpha: 0.4),
                border: const OutlineInputBorder(),
                suffixIcon: const Icon(Icons.lock_outline, color: Colors.teal),
                helperText:
                    'Total belanja kasir: Total Harga dikurangi Total Discount.',
                helperMaxLines: 2,
              ),
            ),
            const SizedBox(height: 24),

            FilledButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check_circle_outline),
              label: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(
                  isEditingExisting ? 'Simpan Perubahan' : 'Simpan Transaksi',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
