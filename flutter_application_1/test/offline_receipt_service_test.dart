import 'package:flutter_test/flutter_test.dart';
import 'package:receipt_scanner_app/services/offline_receipt_service.dart';

void main() {
  test('OfflineReceiptService parses Alfamart receipt with multi-number and total item', () {
    const sampleOcr = '''
ALFAMART JALAPRANG / 081294657636
JALAPRANG [JLP]
ALFA TOWER LT. 12, ALAM SUTERA, TANGERANG
NPUP : 01.336.238.9-054.000
JL JALAPRANG NO. 20 RT 03 RW CIBEUNYING
Bon B101-313-09097836 Kasir : AGHI
SR TUR SP J555G 1 18.000 18.000
KP BRANDING (M) 1 200 200
KP BRANDING (M) -1 200 -200
Total Item 1 18.000
Tunai 100.000
Kembalian 82.000
PPN DPP: 16.216 PPN: 1.783
Tgl. 09-09-2026 18:29:51 V.2026.7.1
KRITIK&SARAN: 1500959
SHS/VA: 081110640888
''';

    final result = OfflineReceiptService.parseReceiptText(sampleOcr, '/dummy/path.jpg');

    expect(result.transaction.storeName, contains('ALFAMART'));
    expect(result.transaction.totalAmount, equals(18000.0));
    expect(result.transaction.transactionDate.year, equals(2026));
    expect(result.transaction.transactionDate.month, equals(9));
    expect(result.transaction.transactionDate.day, equals(9));
    expect(result.transaction.items.isNotEmpty, isTrue);

    final itemNames = result.transaction.items.map((e) => e.itemName).toList();
    expect(itemNames.any((n) => n.contains('SR TUR')), isTrue);
    expect(itemNames.any((n) => n.contains('SHS') || n.contains('SMS')), isFalse);
    expect(result.rawOutput, contains('<s_total_price>18000</s_total_price>'));
  });

  test('OfflineReceiptService parses Alfamart Gardenia with weights (250G, 75G) and ShopeePay', () {
    const gardeniaOcr = '''
ALFAMART PERMATA GARDENIA / 081294660223
NPWP : -
Bon CE35-203-2011VM24 Kasir : HERTI HE
ALFA K.HJ 250G 1 9.600 9.600
INDOMIE KOYA75G 1 2.600 2.600
Total Item 2 12.200
SHOPEEPAY 12.200
Kembalian 0
PPN ( 1.109)
Tgl. 20-11-2020 12:29:58 V.2020.9.3
Member : ROSALYA WIDIANAWATI
POIN MEMBER ANDA 15075
Selamat Poin Member Anda Bertambah 55
Kritik&Saran: 1500959, SMS: 0817111234
''';

    final result = OfflineReceiptService.parseReceiptText(gardeniaOcr, '/dummy/path2.jpg');
    expect(result.transaction.storeName, contains('ALFAMART PERMATA GARDENIA'));
    expect(result.transaction.totalAmount, equals(12200.0));
    expect(result.transaction.transactionDate.year, equals(2020));
    expect(result.transaction.transactionDate.month, equals(11));
    expect(result.transaction.transactionDate.day, equals(20));
    expect(result.transaction.items.length, equals(2));
    expect(result.transaction.items[0].itemName, contains('ALFA K.HJ 250G'));
    expect(result.transaction.items[0].itemPrice, equals(9600.0));
    expect(result.transaction.items[1].itemName, contains('INDOMIE KOYA75G'));
    expect(result.transaction.items[1].itemPrice, equals(2600.0));
  });

  test('OfflineReceiptService parses OCR edge-cases: RLFA typo, Total! Iten, and trailing noise', () {
    const rawNoisyOcr = '''
RLFAYART JALAPRANG / 081294657636
ALFA TOWER LT. 12
Bon B101-313-09097836 Kasir : AGHI
SR THR SP J5556 1 18,000
KP BRANDIHG (H) 1 200 200
KP BRANDING (H) -1 200 -200
Total! Iten 1 18.000
Tunai 100.000
Kenbaliart 82.000
''';

    final result = OfflineReceiptService.parseReceiptText(rawNoisyOcr, '/dummy/noisy.jpg');
    expect(result.transaction.storeName, equals('ALFAMART JALAPRANG'));
    expect(result.transaction.totalAmount, equals(18000.0));
    // Item 1: Qty 1 is stripped from itemName
    expect(result.transaction.items[0].itemName, equals('SR THR SP J5556'));
    expect(result.transaction.items[0].itemPrice, equals(18000.0));
    expect(result.transaction.items[0].quantity, equals(1));
    // Negative plastic bag excluded
    expect(result.transaction.items.any((it) => it.itemName.contains('Total')), isFalse);
  });

  test('OfflineReceiptService parses Gardenia with paper edge noise 9, and split tokens', () {
    const noisyGardenia = '''
ALFAMART PERMATA GARDENIA / 081294660223
NPWP : -
Bon CE35-203-2011VM24 Kasir : HERTI HE
ALFA K.HJ 250G 1 9,600 9,
INDOHIE KOYA75G 1 2600 2600
Total! Iten 2 12.200
SHOPEEPAY 12.200
Kembalian 0
''';

    final result = OfflineReceiptService.parseReceiptText(noisyGardenia, '/dummy/noisy2.jpg');
    expect(result.transaction.storeName, equals('ALFAMART PERMATA GARDENIA'));
    expect(result.transaction.totalAmount, equals(12200.0));
    expect(result.transaction.items[0].itemName, equals('ALFA K.HJ 250G'));
    expect(result.transaction.items[0].itemPrice, equals(9600.0));
    expect(result.transaction.items[0].quantity, equals(1));
    expect(result.transaction.items[1].itemName, equals('INDOHIE KOYA75G'));
    expect(result.transaction.items[1].itemPrice, equals(2600.0));
  });

  test('OfflineReceiptService extracts dates accurately across 4 real receipt variations', () {
    // 1. Karis Jaya Shop: Tanggal dan Jam di dua baris terpisah
    final dateKaris = OfflineReceiptService.extractReceiptDateTime([
      'Karis Jaya Shop',
      '2023-08-02',
      '08:46:36',
      'Indomie Goreng 1 lusin x 36,000 Rp 36.000',
    ]);
    expect(dateKaris, isNotNull);
    expect(dateKaris!.year, equals(2023));
    expect(dateKaris.month, equals(8));
    expect(dateKaris.day, equals(2));
    expect(dateKaris.hour, equals(8));
    expect(dateKaris.minute, equals(46));
    expect(dateKaris.second, equals(36));

    // 2. Indomaret Jatinangor: DD. MM. YY dengan spasi
    final dateIndo1 = OfflineReceiptService.extractReceiptDateTime([
      'INDOMARET JATINANGOR KM. 20',
      '14. 09. 16 - 06:46',
      'S/ROTI KRIM KEJU 72G 4 4500 18,000',
    ]);
    expect(dateIndo1, isNotNull);
    expect(dateIndo1!.year, equals(2016));
    expect(dateIndo1.month, equals(9));
    expect(dateIndo1.day, equals(14));
    expect(dateIndo1.hour, equals(6));
    expect(dateIndo1.minute, equals(46));

    // 3. Indomaret Lampung: Tanggal rapat menyatu dengan kode POS
    final dateIndo2 = OfflineReceiptService.extractReceiptDateTime([
      'PT.INDOMARCO PRISMATAMA',
      '04.04.24-12:22/3.0.13/T3E0 1457/NI MA/02',
      'HAPPY NAPPY PANT 28L 2 49900 99,800',
    ]);
    expect(dateIndo2, isNotNull);
    expect(dateIndo2!.year, equals(2024));
    expect(dateIndo2.month, equals(4));
    expect(dateIndo2.day, equals(4));
    expect(dateIndo2.hour, equals(12));
    expect(dateIndo2.minute, equals(22));

    // 4. Struk Duplikat: Tanggal di baris footer paling bawah
    final dateDuplikat = OfflineReceiptService.extractReceiptDateTime([
      'D U P L I K A T',
      'Bon: 1VM5-789-2210WKW7',
      'KP BRD L 0.020 1 500 500',
      'Total Item 4 24,600',
      'Tunai 24,600',
      'Tgl. 22-10-2022 15:36:43',
    ]);
    expect(dateDuplikat, isNotNull);
    expect(dateDuplikat!.year, equals(2022));
    expect(dateDuplikat.month, equals(10));
    expect(dateDuplikat.day, equals(22));
    expect(dateDuplikat.hour, equals(15));
    expect(dateDuplikat.minute, equals(36));
    expect(dateDuplikat.second, equals(43));
  });

  test('OfflineReceiptService filters VC voucher lines and non-tunai in Indomaret receipts', () {
    const indomaretOcr = '''
INDOMARET SOEKARNO HATTA
04.04.24-12:22/3.0.13/T3E0
HAPPY NAPPY PANT 28L 2 49900 99,800
VC SOFTEX INDONE : (10,000)
IDM KTG PLSTK 1W BSR 2 300 600
VC DIAPERS FAIR/INDOMARCO PRI : (15,000)
HARGA JUAL : 75,400
TOTAL : 75,400
NON TUNAI : 75,400
ANDA HEMAT : 25,000
PPN : DPP= 90,450 PPN= 9,950
LAYANAN KONSUMEN SMS/WA 0811 1500 280
''';

    final result = OfflineReceiptService.parseReceiptText(indomaretOcr, '/dummy/indo.jpg');
    expect(result.transaction.storeName, contains('INDOMARET'));
    expect(result.transaction.totalAmount, equals(75400.0));
    expect(result.transaction.items.length, equals(2));
    expect(result.transaction.items[0].itemName, contains('HAPPY NAPPY'));
    expect(result.transaction.items[0].quantity, equals(2));
    expect(result.transaction.items[0].itemPrice, equals(49900.0));
    expect(result.transaction.items[0].subtotal, equals(99800.0));
    expect(result.transaction.items[1].itemName, contains('IDM KTG PLSTK'));
    expect(result.transaction.items[1].quantity, equals(2));
    expect(result.transaction.items[1].itemPrice, equals(300.0));
    expect(result.transaction.items[1].subtotal, equals(600.0));
    // Make sure VC and HARGA JUAL are NOT included as items
    expect(result.transaction.items.any((it) => it.itemName.contains('VC ')), isFalse);
    expect(result.transaction.items.any((it) => it.itemName.contains('HARGA JUAL')), isFalse);
    expect(result.transaction.items.any((it) => it.itemName.contains('NON TUNAI')), isFalse);
  });

  test('OfflineReceiptService parses Indomaret modern digital receipt with corporate header and branch reconstruction', () {
    const indomaretCikawung = '''
Struk Transaksi
PT.INDOMARCO PRISMATAMA
GEDUNG MENARA INDOMARET
BOULEVARD PANTAI INDAH KAPUK
JAKARTA UTARA
NPWP:001.337.994.6-092.000
CIKAWUNG
JL RAYA LASWI NO 316, KEL WARGAMEKAR
KEC BALEENDAH, KAB BANDUNG, 40375
18.08.26-15:46/4.4.2/THL5-349/MUHAM/01
IDM KTG PLSTK 1W BSR 1 500 500
PEPSODENT COMP8 150G 1 15000 15,000
VOUCHER : (2,500)
LFBY CC PRG LME2X610 1 14000 14,000
NVEA MEN ROLL EPC 50 1 25300 25,300
VOUCHER : (8,400)
LARISST CLK LIME 370 2 5500 11,000
TOTAL BELANJA : 54,900
TUNAI : 100,000
KEMBALI : 45,100
ANDA HEMAT : 10,900
PPN : DPP= 54,339 PPN= 6,521
HARGA JUAL : 59,279
ID POINKU : xxxxxxxxx4143/KHxxxxx Axxxxxx x
CEK POIN/STAMP/LUCKY DI APPS POINKU
LAYANAN KONSUMEN
''';

    final res = OfflineReceiptService.parseReceiptText(indomaretCikawung, null);
    expect(res.transaction.storeName, equals('INDOMARET CIKAWUNG'));
    expect(res.transaction.totalAmount, equals(54900.0));
    expect(res.transaction.transactionDate.year, equals(2026));
    expect(res.transaction.transactionDate.month, equals(8));
    expect(res.transaction.transactionDate.day, equals(18));
    expect(res.transaction.transactionDate.hour, equals(15));
    expect(res.transaction.transactionDate.minute, equals(46));
    expect(res.transaction.items.length, equals(5));
    expect(res.transaction.items.any((it) => it.itemName.contains('KEC')), isFalse);
    expect(res.transaction.items.any((it) => it.itemName.contains('MENARA')), isFalse);
  });

  test('OfflineReceiptService handles 100% discount / Total Belanja 0 accurately', () {
    const promoReceipt = '''
Struk Transaksi
PT.INDOMARCO PRISMATAMA
GEDUNG MENARA INDOMARET
BOULEVARD PANTAI INDAH KAPUK
JAKARTA UTARA
NPWP:001.337.994.6-092.000
CIPARAY 671
JL LASWI NO 671, KEL SARIMAHI
KEC CIPARAY, KAB BANDUNG, 40381
16.09.26-06:58/4.4.2/T08T-349/KARIM/01
YCG MTCHA SEASLT ICE 1 15000 15,000
DISKON : (15,000)
TOTAL BELANJA : 0
ANDA HEMAT : 15,000
HARGA JUAL : 0
ID POINKU : xxxxxxxx4143/KHxxxx Axxxxxx x
CEK POIN/STAMP/LUCKY DI APPS POINKU
LAYANAN KONSUMEN
''';

    final res = OfflineReceiptService.parseReceiptText(promoReceipt, null);
    expect(res.transaction.storeName, equals('INDOMARET CIPARAY 671'));
    expect(res.transaction.totalAmount, equals(0.0));
    expect(res.transaction.items.length, equals(1));
    expect(res.transaction.items[0].itemName, contains('MTCHA SEASLT'));
  });

  test('OfflineReceiptService prioritizes Grand Total over Subtotal and flags estimated date', () {
    const receiptWithMultiTotals = '''
CAFE KOPI KENANGAN
ROTI BAKAR COKLAT 1 25.000
SUBTOTAL : 25.000
PAJAK PB1 : 2.500
GRAND TOTAL : 27.500
TUNAI : 30.000
KEMBALI : 2.500
''';
    final res = OfflineReceiptService.parseReceiptText(receiptWithMultiTotals, null);
    expect(res.transaction.totalAmount, equals(27500.0));
    expect(res.isDateEstimated, isTrue);
  });
}
