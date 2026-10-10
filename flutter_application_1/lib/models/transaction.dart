import 'transaction_item.dart';

/// Model untuk satu baris pada tabel `transactions` (BAB 3.3), beserta
/// daftar item-nya (join ke `transaction_items`) untuk kebutuhan tampilan.
class Transaction {
  final int? id;
  final String storeName;
  final String category;
  final double totalAmount;
  final DateTime transactionDate;
  final String? imagePath;
  final DateTime createdAt;
  final List<TransactionItem> items;

  Transaction({
    this.id,
    required this.storeName,
    this.category = 'Belanja Harian',
    required this.totalAmount,
    required this.transactionDate,
    this.imagePath,
    DateTime? createdAt,
    this.items = const [],
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'store_name': storeName,
      'category': category,
      'total_amount': totalAmount,
      'transaction_date': transactionDate.toIso8601String(),
      'image_path': imagePath,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory Transaction.fromMap(
    Map<String, dynamic> map, {
    List<TransactionItem> items = const [],
  }) {
    return Transaction(
      id: map['id'] as int?,
      storeName: map['store_name'] as String? ?? 'Toko Tidak Dikenal',
      category: map['category'] as String? ?? 'Belanja Harian',
      totalAmount: (map['total_amount'] as num?)?.toDouble() ?? 0,
      transactionDate:
          DateTime.tryParse(map['transaction_date'] as String? ?? '') ??
              DateTime.now(),
      imagePath: map['image_path'] as String?,
      createdAt: DateTime.tryParse(map['created_at'] as String? ?? '') ??
          DateTime.now(),
      items: items,
    );
  }

  double get itemsTotal => items.fold(0, (sum, item) => sum + item.subtotal);

  Transaction copyWith({
    int? id,
    String? storeName,
    String? category,
    double? totalAmount,
    DateTime? transactionDate,
    String? imagePath,
    List<TransactionItem>? items,
  }) {
    return Transaction(
      id: id ?? this.id,
      storeName: storeName ?? this.storeName,
      category: category ?? this.category,
      totalAmount: totalAmount ?? this.totalAmount,
      transactionDate: transactionDate ?? this.transactionDate,
      imagePath: imagePath ?? this.imagePath,
      createdAt: createdAt,
      items: items ?? this.items,
    );
  }
}
