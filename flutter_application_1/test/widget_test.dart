// Test bawaan `flutter create` (widget_test.dart) sebelumnya mereferensikan
// `MyApp` dari template counter-app default, yang sudah diganti oleh
// `ReceiptScannerApp`. File ini diganti dengan placeholder sederhana supaya
// `flutter analyze` / `flutter test` bersih.
//
// Catatan: DashboardScreen memanggil DatabaseHelper (sqflite) dan
// ScannerScreen memakai CameraController di initState, yang butuh platform
// channel (mis. sqflite_common_ffi untuk test) untuk bisa di-pump penuh di
// widget test. Menulis test end-to-end untuk layar-layar itu perlu setup
// mocking tambahan — di luar cakupan skeleton ini untuk saat ini.
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:receipt_scanner_app/utils/currency_format_helper.dart';

void main() {
  test('CurrencyFormatHelper test', () async {
    await initializeDateFormatting('id_ID', null);
    expect(CurrencyFormatHelper.formatReceipt(18000), equals('18.000'));
    expect(CurrencyFormatHelper.formatReceipt(0), equals('0'));
    expect(CurrencyFormatHelper.formatRp(18000), equals('Rp 18.000'));
    expect(CurrencyFormatHelper.parsePrice('18.000'), equals(18000.0));
  });
}
