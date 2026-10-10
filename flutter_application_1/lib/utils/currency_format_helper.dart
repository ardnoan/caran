import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

/// Helper pemformatan dan parsing nilai uang sesuai standar struk kasir Indonesia.
///
/// Contoh:
/// - formatReceipt(18000) -> "18.000"
/// - formatReceipt(-200) -> "-200"
/// - formatRp(18000) -> "Rp 18.000"
/// - formatRp(-200) -> "-Rp 200"
/// - parsePrice("18.000") -> 18000.0
/// - parsePrice("Rp 18.000") -> 18000.0
/// - parsePrice("-200") -> -200.0
class CurrencyFormatHelper {
  static final NumberFormat _receiptFormatter = NumberFormat('#,##0', 'id_ID');

  /// Format angka sesuai tampilan pada struk fisik kasir (misal: "18.000" atau "-200")
  static String formatReceipt(double amount) {
    if (amount < 0) {
      return '-${_receiptFormatter.format(amount.abs().round())}';
    }
    return _receiptFormatter.format(amount.round());
  }

  /// Format angka dengan awalan simbol Rupiah (misal: "Rp 18.000" atau "-Rp 200")
  static String formatRp(double amount) {
    if (amount < 0) {
      return '-Rp ${_receiptFormatter.format(amount.abs().round())}';
    }
    return 'Rp ${_receiptFormatter.format(amount.round())}';
  }

  /// Parsing angka dari input teks struk / user yang mungkin mengandung titik, koma, spasi, atau teks 'Rp'
  static double parsePrice(String text) {
    var s = text.trim();
    if (s.isEmpty) return 0.0;

    final isNegative = s.contains('-') || s.startsWith('(');

    // Hapus karakter selain digit, minus, titik, dan koma
    s = s.replaceAll(RegExp(r'[^0-9.,]'), '');
    if (s.isEmpty) return 0.0;

    // Normalisasi pemisah ribuan dan desimal gaya Indonesia
    if (s.contains('.') && s.contains(',')) {
      // Format 18.000,50 -> 18000.50
      s = s.replaceAll('.', '').replaceAll(',', '.');
    } else if (s.contains('.')) {
      // Format 18.000 -> 18000
      final parts = s.split('.');
      if (parts.length > 2 || (parts.length == 2 && parts[1].length == 3)) {
        s = s.replaceAll('.', '');
      }
    } else if (s.contains(',')) {
      // Format 18,000 -> 18000
      final parts = s.split(',');
      if (parts.length > 2 || (parts.length == 2 && parts[1].length == 3)) {
        s = s.replaceAll(',', '');
      } else {
        s = s.replaceAll(',', '.');
      }
    }

    final val = double.tryParse(s) ?? 0.0;
    return isNegative ? -val.abs() : val;
  }
}

/// Formatter input teks secara real-time yang memformat angka dengan pemisah ribuan
/// gaya Indonesia (titik) saat pengguna mengetik nilai uang (misal: 18000 -> 18.000).
class CurrencyTextInputFormatter extends TextInputFormatter {
  CurrencyTextInputFormatter({this.allowNegative = true});

  final bool allowNegative;
  static final NumberFormat _formatter = NumberFormat('#,##0', 'id_ID');

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    if (newValue.text.isEmpty) {
      return newValue;
    }

    final isNegative = allowNegative && (newValue.text.startsWith('-') || newValue.text.startsWith('('));
    // Ambil hanya digit angka
    final digitsOnly = newValue.text.replaceAll(RegExp(r'[^0-9]'), '');
    if (digitsOnly.isEmpty) {
      return isNegative
          ? const TextEditingValue(text: '-', selection: TextSelection.collapsed(offset: 1))
          : const TextEditingValue(text: '', selection: TextSelection.collapsed(offset: 0));
    }

    final number = int.tryParse(digitsOnly);
    if (number == null) return oldValue;

    final formatted = _formatter.format(number);
    final resultText = isNegative ? '-$formatted' : formatted;

    return TextEditingValue(
      text: resultText,
      selection: TextSelection.collapsed(offset: resultText.length),
    );
  }
}
