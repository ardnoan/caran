import 'dart:io';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../db/database_helper.dart';
import '../models/transaction.dart';
import '../utils/currency_format_helper.dart';
import 'preview_edit_screen.dart';

/// Halaman Detail Rincian Barang / Itemized View (BAB 4.2 poin 3).
class ItemDetailScreen extends StatefulWidget {
  const ItemDetailScreen({super.key, required this.transactionId});

  final int transactionId;

  @override
  State<ItemDetailScreen> createState() => _ItemDetailScreenState();
}

class _ItemDetailScreenState extends State<ItemDetailScreen> {
  Transaction? _transaction;
  final _dateFormat = DateFormat('d MMMM yyyy, HH:mm', 'id_ID');

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final trx = await DatabaseHelper.instance.getTransactionWithItems(widget.transactionId);
    if (mounted) setState(() => _transaction = trx);
  }

  @override
  Widget build(BuildContext context) {
    final trx = _transaction;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detail Transaksi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            tooltip: 'Edit Transaksi',
            onPressed: () async {
              if (_transaction == null) return;
              final updated = await Navigator.of(context).push<bool>(
                MaterialPageRoute(
                  builder: (_) => PreviewEditScreen(
                    transaction: _transaction!,
                  ),
                ),
              );
              if (updated == true && mounted) {
                _load();
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.red),
            tooltip: 'Hapus Transaksi',
            onPressed: () async {
              final nav = Navigator.of(context);
              final confirm = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Hapus Transaksi?'),
                  content: const Text(
                      'Data transaksi beserta rincian barangnya akan dihapus secara permanen.'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Batal'),
                    ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Hapus'),
                    ),
                  ],
                ),
              );

              if (confirm == true) {
                await DatabaseHelper.instance.deleteTransaction(widget.transactionId);
                nav.pop(true);
              }
            },
          ),
        ],
      ),
      body: trx == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(trx.storeName, style: Theme.of(context).textTheme.headlineSmall),
                          const SizedBox(height: 4),
                          Text(_dateFormat.format(trx.transactionDate),
                              style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                    Chip(
                      avatar: const Icon(Icons.label_outline, size: 16, color: Colors.teal),
                      label: Text(trx.category, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                      backgroundColor: Colors.teal.shade50,
                      side: BorderSide(color: Colors.teal.shade200),
                    ),
                  ],
                ),
                const Divider(height: 32),
                ...trx.items.map((item) {
                  final isDiscount = item.itemPrice < 0 || item.itemName.toLowerCase().contains('potongan');
                  if (isDiscount) {
                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const CircleAvatar(
                        radius: 14,
                        backgroundColor: Color(0xFFFFF3E0),
                        child: Icon(Icons.local_offer_outlined, size: 14, color: Colors.orange),
                      ),
                      title: Text(
                        item.itemName,
                        style: TextStyle(fontWeight: FontWeight.w600, color: Colors.orange.shade900),
                      ),
                      subtitle: const Text('Potongan voucher / promo kasir', style: TextStyle(fontSize: 11)),
                      trailing: Text(
                        '- ${CurrencyFormatHelper.formatRp(item.subtotal.abs())}',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red),
                      ),
                    );
                  }
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(item.itemName),
                    subtitle: Text('${item.quantity} x ${CurrencyFormatHelper.formatRp(item.itemPrice)}'),
                    trailing: Text(CurrencyFormatHelper.formatRp(item.subtotal)),
                  );
                }),
                const Divider(height: 32),
                Builder(
                  builder: (context) {
                    final gross = trx.items
                        .where((it) => it.itemPrice > 0 && !it.itemName.toLowerCase().contains('potongan'))
                        .fold(0.0, (sum, it) => sum + it.subtotal);
                    final discount = trx.items
                        .where((it) => it.itemPrice < 0 || it.itemName.toLowerCase().contains('potongan'))
                        .fold(0.0, (sum, it) => sum + it.subtotal.abs());

                    if (discount > 0.01) {
                      return Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Total Harga', style: TextStyle(fontSize: 14, color: Colors.grey.shade700)),
                              Text(CurrencyFormatHelper.formatRp(gross),
                                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey.shade800)),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Total Discount', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.amber.shade900)),
                              Text('- ${CurrencyFormatHelper.formatRp(discount)}',
                                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.red)),
                            ],
                          ),
                          const Divider(height: 24),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Total Belanja', style: Theme.of(context).textTheme.titleLarge),
                              Text(CurrencyFormatHelper.formatRp(trx.totalAmount),
                                  style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: Colors.teal.shade900)),
                            ],
                          ),
                        ],
                      );
                    }

                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Total Belanja', style: Theme.of(context).textTheme.titleLarge),
                        Text(CurrencyFormatHelper.formatRp(trx.totalAmount),
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: Colors.teal.shade900)),
                      ],
                    );
                  },
                ),
                if (trx.imagePath != null && File(trx.imagePath!).existsSync()) ...[
                  const Divider(height: 32),
                  const Text(
                    'Foto Struk Belanja Asli',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey.shade300),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      constraints: const BoxConstraints(maxHeight: 280),
                      width: double.infinity,
                      child: Image.file(
                        File(trx.imagePath!),
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),
                ],
              ],
            ),
    );
  }
}
