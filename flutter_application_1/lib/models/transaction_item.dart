/// Model untuk satu baris pada tabel `transaction_items` (BAB 3.3).
class TransactionItem {
  final int? id;
  final int? transactionId;
  final String itemName;
  final double itemPrice;
  final int quantity;

  TransactionItem({
    this.id,
    this.transactionId,
    required this.itemName,
    required this.itemPrice,
    this.quantity = 1,
  });

  double get subtotal => itemPrice * quantity;

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'transaction_id': transactionId,
      'item_name': itemName,
      'item_price': itemPrice,
      'quantity': quantity,
    };
  }

  factory TransactionItem.fromMap(Map<String, dynamic> map) {
    return TransactionItem(
      id: map['id'] as int?,
      transactionId: map['transaction_id'] as int?,
      itemName: map['item_name'] as String? ?? '-',
      itemPrice: (map['item_price'] as num?)?.toDouble() ?? 0,
      quantity: (map['quantity'] as num?)?.toInt() ?? 1,
    );
  }

  TransactionItem copyWith({
    int? id,
    int? transactionId,
    String? itemName,
    double? itemPrice,
    int? quantity,
  }) {
    return TransactionItem(
      id: id ?? this.id,
      transactionId: transactionId ?? this.transactionId,
      itemName: itemName ?? this.itemName,
      itemPrice: itemPrice ?? this.itemPrice,
      quantity: quantity ?? this.quantity,
    );
  }
}
