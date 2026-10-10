// ignore_for_file: avoid_print

import 'package:flutter_test/flutter_test.dart';
import 'package:receipt_scanner_app/services/offline_receipt_service.dart';

void main() {
  test('Debug Alfamart Digital Receipt 1 (Jalaprang)', () {
    const rawText1 = '''
ALFAMART
ALFAMART JALAPRANG / 081294657636
JALAPRANG [JLP]
ALFA TOWER LT.12, ALAM SUTERA,TANGERANG
NPWP : 01.336.238.9-054.000
JL JALAPRANG NO. 20 RT 03 RW CIBEUNYING
Bon B101-313-0610H7Z5 Kasir : AGHI
INDOMIE AYMI27G 1 4,300 4,300
INDOMIE RDG120G 1 4,300 4,300
INDOMIE IJO120G 1 4,300 4,300
INDOMIE ACH 90G 1 3,300 3,300
INDOMIE GPRK85G 1 3,400 3,400
KP BRANDING (M) 1 200 200
Total Item 6 19,800
QRIS SOUNDBOX 19,800
Kembalian 0
DPP : 17,837 PPN : 1,962
Tgl. 06-10-2026 17:30:51 V.2026.7.2
MEMBER : SAKHA *****
A-POIN ANDA 9622
459 poin Anda akan expired pada 31-Dec-2027
STRUK ANDA AKAN DIKIRIM KE APLIKASI ALFAGIFT
Potensi Poin Jika Anda Member 89
KHUSUS MEMBER ULTAH
Potongan Rp5.000
Belanja ALL PRODUK (kec minyak,rokok,gula,beras&susu <1thn)
min Rp75.000 dg kode (C0577B26B2UZ)
s/d 31 Oktober 2026
KRITIK&SARAN: 1500959
SMS/WA: 081110640888
''';

    final res1 = OfflineReceiptService.parseReceiptText(rawText1, null);
    expect(res1.transaction.storeName, equals('ALFAMART JALAPRANG'));
    expect(res1.transaction.totalAmount, equals(19800.0));
    expect(res1.transaction.transactionDate.year, equals(2026));
    expect(res1.transaction.transactionDate.month, equals(10));
    expect(res1.transaction.transactionDate.day, equals(6));
    expect(res1.transaction.transactionDate.hour, equals(17));
    expect(res1.transaction.transactionDate.minute, equals(30));
    expect(res1.isDateEstimated, isFalse);
    expect(res1.transaction.items.length, equals(6));
    expect(res1.transaction.items.any((it) => it.itemName.contains('Potongan')), isFalse);
    expect(res1.transaction.items.any((it) => it.itemName.contains('kode')), isFalse);
  });

  test('Debug Alfamart Digital Receipt 2 (Karang Potong with Discounts)', () {
    const rawText2 = '''
ALFAMART
ALFAMART KARANG POTONG
KARANG POTONG/F [KAPG]
CV. HDJ BERKAH ABADI
KAMPUNG SEDEKAN RT. 002 RW. 005
NPWP : 53.599.441.2-406.000
Bon 2JR9-113-300845H2 Kasir : ACEK R
WLS PLCHO90ML/D 3 5,900 17,700
-900
CALADINE LOT 60 1 23,100 23,100
CADBURY CRSP52G 1 19,000 19,000
-2,300
Total Item 3 59,800
Total Disc. 3,200
Total Belanja 56,600
QRIS BRI BRIMO 56,600
Kembalian 0
DPP: 52,612 PPN: 5,787
Tgl. 30-08-2026 13:53:10 V.2026.5.2
MEMBER : SAKHA *****
A-POIN ANDA 9368
459 poin Anda akan expired pada 31-Dec-2027
STRUK ANDA AKAN DIKIRIM KE APLIKASI ALFAGIFT
Potensi Poin Jika Anda Member 254
KRITIK&SARAN:1500959
SMS/WA: 081110640888
''';

    final res2 = OfflineReceiptService.parseReceiptText(rawText2, null);
    expect(res2.transaction.storeName, equals('ALFAMART KARANG POTONG'));
    expect(res2.transaction.totalAmount, equals(56600.0));
    expect(res2.transaction.transactionDate.year, equals(2026));
    expect(res2.transaction.transactionDate.month, equals(8));
    expect(res2.transaction.transactionDate.day, equals(30));
    expect(res2.isDateEstimated, isFalse);
    expect(res2.transaction.items.length, equals(5));
    final sumItems2 = res2.transaction.items.fold(0.0, (sum, it) => sum + it.subtotal);
    expect(sumItems2, equals(56600.0));
  });

  test('Debug Alfamart Digital Receipt 4 (Karang Potong 4 with WLS OREO 90ML 3)', () {
    const rawText4 = '''
ALFAMART
ALFAMART KARANG POTONG
KARANG POTONG/F [KAPG]
CV. HDJ BERKAH ABADI
KAMPUNG SEDEKAN RT. 002 RW. 005
NPWP : 53.599.441.2-406.000
Bon 2JR9-201-1207WV89 Kasir : MUHAMA
POWERADE B400ML 1 6,000 6,000
-500
NSCF ROAST 10S 1 15,400 15,400
PROCHIZ GLD160G 1 16,600 16,600
-3,400
WLS OREO 90ML 3 9,800 29,400
-800
WLS PP SHK150ML 1 11,800 11,800
PEPSO SWK150+25 1 21,200 21,200
-11,200
Total Item 6 100,400
Total Disc. 15,900
Total Belanja 84,500
QRIS BRI BRIMO 84,500
Kembalian 0
DPP: 89,369 PPN: 9,830
Tgl. 12-07-2026 14:06:22 V.2026.5.1
MEMBER : SAKHA *****
A-POIN ANDA 8194
459 poin Anda akan expired pada 31-Dec-2027
STRUK ANDA AKAN DIKIRIM KE APLIKASI ALFAGIFT
Potensi Poin Jika Anda Member 373
KRITIK&SARAN:1500959
SMS/WA: 081110640888
''';

    final res4 = OfflineReceiptService.parseReceiptText(rawText4, null);
    expect(res4.transaction.storeName, equals('ALFAMART KARANG POTONG'));
    expect(res4.transaction.totalAmount, equals(84500.0));
    expect(res4.transaction.transactionDate.year, equals(2026));
    expect(res4.transaction.transactionDate.month, equals(7));
    expect(res4.transaction.transactionDate.day, equals(12));
    expect(res4.isDateEstimated, isFalse);
    expect(res4.transaction.items.length, equals(10));
    final sumItems4 = res4.transaction.items.fold(0.0, (sum, it) => sum + it.subtotal);
    expect(sumItems4, equals(84500.0));

    final oreoItem = res4.transaction.items.firstWhere((it) => it.itemName == 'WLS OREO 90ML');
    expect(oreoItem.quantity, equals(3));
    expect(oreoItem.itemPrice, equals(9800.0));
    expect(oreoItem.subtotal, equals(29400.0));

    final oreoDiscount = res4.transaction.items.firstWhere((it) => it.itemName.contains('Potongan: WLS OREO'));
    expect(oreoDiscount.quantity, equals(1));
    expect(oreoDiscount.itemPrice, equals(-800.0));
    expect(oreoDiscount.subtotal, equals(-800.0));

    final pepsoItem = res4.transaction.items.firstWhere((it) => it.itemName.contains('PEPSO'));
    expect(pepsoItem.quantity, equals(1));
    expect(pepsoItem.itemPrice, equals(21200.0));
    expect(pepsoItem.subtotal, equals(21200.0));
  });

  test('Debug Alfamart Receipt 5 (Karang Potong with Softex, Me-O, KG SLT)', () {
    const rawText5 = '''
ALFAMART
ALFAMART KARANG POTONG
KARANG POTONG/F [KAPG]
CV. HDJ BERKAH ABADI
KAMPUNG SEDEKAN RT. 002 RW. 005
NPWP : 53.599.441.2-406.000
Bon 2JR9-113-1707Z2Y5 Kasir : ACEK R
ALFAMRT ECO PB 1 2,000 2,000
SOFTEX W23CM30P 1 28,900 28,900
Disc. -3,000
INDOMIE KARI70G 2 3,300 6,600
NS WLN CHO 100G 1 11,800 11,800
ME-O TUNA 200G 1 20,500 20,500
Disc. -5,000
KG SLT CHS200G 1 13,900 13,900
Disc. -2,400
Total Item 6 83,700
Total Disc. 10,400
Total Belanja 73,300
QRIS BRI BRIMO 73,300
Kembalian 0
DPP: 75,135 PPN: 8,264
Tgl. 17-07-2026 17:28:06 V.2026.5.2
MEMBER : SAKHA *****
A-POIN ANDA 8658
459 poin Anda akan expired pada 31-Dec-2027
STRUK ANDA AKAN DIKIR KE APLIKASI ALFAGIFT
Potensi Poin Jika Anda Member 325
KRITIK&SARAN: 1500959
SMS/WA: 081110640888
''';

    final res5 = OfflineReceiptService.parseReceiptText(rawText5, null);
    print('=== RECEIPT 5 ===');
    print('Store: ${res5.transaction.storeName}');
    print('Total: ${res5.transaction.totalAmount}');
    print('Date: ${res5.transaction.transactionDate}');
    print('Items count: ${res5.transaction.items.length}');
    for (var i = 0; i < res5.transaction.items.length; i++) {
      final it = res5.transaction.items[i];
      print('[$i] "${it.itemName}" | Qty: ${it.quantity} | Price: ${it.itemPrice} | Subtotal: ${it.subtotal}');
    }
    final sum = res5.transaction.items.fold(0.0, (s, it) => s + it.subtotal);
    print('Sum of items: $sum');
  });

  test('Debug Alfamart Digital Receipt 3 (Karang Potong 2 items)', () {
    const rawText3 = '''
ALFAMART
ALFAMART KARANG POTONG
KARANG POTONG/F [KAPG]
CV. HDJ BERKAH ABADI
KAMPUNG SEDEKAN RT. 002 RW. 005
NPWP : 53.599.441.2-406.000
Bon 2JR9-201-2407WCX5 Kasir : MUHAMA
NSCF ROAST 10S 1 15,400 15,400
FRESCO CPCN 9S 1 15,000 15,000
Total Item 2 30,400
DANA QRIS 30,400
Kembalian 0
DPP: 27,387 PPN: 3,012
Tgl. 24-07-2026 08:04:44 V.2026.5.2
MEMBER : SAKHA *****
Potensi Poin Jika Anda Member 136
KRITIK&SARAN:1500959
SMS/WA: 081110640888
''';

    final res3 = OfflineReceiptService.parseReceiptText(rawText3, null);
    expect(res3.transaction.storeName, equals('ALFAMART KARANG POTONG'));
    expect(res3.transaction.totalAmount, equals(30400.0));
    expect(res3.transaction.transactionDate.year, equals(2026));
    expect(res3.transaction.transactionDate.month, equals(7));
    expect(res3.transaction.transactionDate.day, equals(24));
    expect(res3.isDateEstimated, isFalse);
    expect(res3.transaction.items.length, equals(2));
    final sumItems3 = res3.transaction.items.fold(0.0, (sum, it) => sum + it.subtotal);
    expect(sumItems3, equals(30400.0));
  });
}
