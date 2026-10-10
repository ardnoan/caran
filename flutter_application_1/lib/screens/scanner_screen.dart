// =============================================================================
// ALUR SISTEM: SCANNER SCREEN (AKUISISI CITRA STRUK FISIK)
// =============================================================================
// Peran dalam Arsitektur:
// 1. INPUT:
//    - Sensor kamera belakang HP (kualitas Full HD / ResolutionPreset.high)
//    - Atau file gambar dari galeri HP (ImagePicker)
// 2. KONTROL PENGGUNA:
//    - Viewfinder bingkai panduan visual untuk memposisikan struk tegak lurus
//    - Tombol Senter (Torch Lighting) untuk menerangi struk di tempat redup
// 3. PROSES:
//    - controller.takePicture() -> menghasilkan file citra .jpg di cache lokal
// 4. OUTPUT:
//    - Navigator.pop(context, shot.path) -> mengembalikan path ke DashboardScreen
//    - DashboardScreen kemudian mengumpankan path ini ke OfflineReceiptService
// =============================================================================

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

/// Halaman Scanner Struk (BAB 4.2 poin 1).
///
/// Mendukung 2 mode input:
/// 1. Kamera langsung (Snapshot manual): Dilengkapi viewfinder / kotak panduan
///    agar struk difoto dari jarak yang pas & teks terbaca tajam.
/// 2. Upload dari Galeri: Pengguna memilih foto struk yang sudah ada dari HP.
class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  CameraController? _controller;
  final _picker = ImagePicker();
  bool _isFlashOn = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) return;

      final backCamera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      final controller = CameraController(
        backCamera,
        ResolutionPreset.high,
        enableAudio: false,
      );
      await controller.initialize();
      if (!mounted) return;
      setState(() => _controller = controller);
    } catch (e) {
      debugPrint('ScannerScreen: Gagal inisialisasi kamera: $e');
    }
  }

  Future<void> _toggleFlash() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) return;

    try {
      final newMode = _isFlashOn ? FlashMode.off : FlashMode.torch;
      await controller.setFlashMode(newMode);
      if (!mounted) return;
      setState(() => _isFlashOn = !_isFlashOn);
    } catch (e) {
      debugPrint('ScannerScreen: Gagal toggle flash: $e');
    }
  }

  Future<void> _captureFromCamera() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) return;

    try {
      final shot = await controller.takePicture();
      if (!mounted) return;
      Navigator.of(context).pop(shot.path);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal mengambil foto: $e')),
        );
      }
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final picked = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
      );
      if (picked != null && mounted) {
        Navigator.of(context).pop(picked.path);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal memilih foto dari galeri: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = _controller;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan / Upload Struk'),
        actions: [
          IconButton(
            icon: Icon(_isFlashOn ? Icons.flash_on : Icons.flash_off,
                color: _isFlashOn ? Colors.amber : null),
            tooltip: _isFlashOn ? 'Matikan Senter' : 'Nyalakan Senter',
            onPressed: _toggleFlash,
          ),
          IconButton(
            icon: const Icon(Icons.photo_library),
            tooltip: 'Upload dari Galeri',
            onPressed: _pickFromGallery,
          ),
        ],
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Preview Kamera dengan Tap to Focus presisi
          if (controller != null && controller.value.isInitialized)
            LayoutBuilder(
              builder: (context, constraints) {
                return GestureDetector(
                  onTapDown: (details) {
                    try {
                      final offset = details.localPosition;
                      final point = Offset(
                        (offset.dx / constraints.maxWidth).clamp(0.0, 1.0),
                        (offset.dy / constraints.maxHeight).clamp(0.0, 1.0),
                      );
                      controller.setFocusPoint(point);
                      controller.setExposurePoint(point);
                    } catch (e) {
                      debugPrint('Focus error: $e');
                    }
                  },
                  child: CameraPreview(controller),
                );
              },
            )
          else
            Container(
              color: Colors.black87,
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text(
                      'Menyiapkan kamera...',
                      style: TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ),

          // 2. Kotak Panduan Struk (Viewfinder Overlay)
          Center(
            child: Container(
              width: MediaQuery.of(context).size.width * 0.88,
              height: MediaQuery.of(context).size.height * 0.72,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.tealAccent, width: 2.5),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    margin: const EdgeInsets.only(top: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.75),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.crop_rotate, color: Colors.tealAccent, size: 14),
                        SizedBox(width: 6),
                        Text(
                          'Posisikan struk tegak lurus searah tulisan (jangan terbalik)',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.65),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Kamera menangkap seluruh struk (tidak terpotong oleh kotak)',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 3. Banner Panduan & Status Model
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Card(
              color: Colors.white.withValues(alpha: 0.94),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Padding(
                padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(
                  children: [
                    Icon(
                      Icons.offline_bolt,
                      color: Colors.teal,
                      size: 22,
                    ),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Mesin Offline-First Siap! Dekatkan kamera ke struk agar tulisan terlihat jelas.',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 4. Tombol Kontrol Bawah (Jepret Foto & Upload Galeri)
          Positioned(
            bottom: 30,
            left: 20,
            right: 20,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                FloatingActionButton.extended(
                  heroTag: 'btn_gallery',
                  onPressed: _pickFromGallery,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galeri'),
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.teal.shade800,
                ),
                FloatingActionButton.large(
                  heroTag: 'btn_capture',
                  onPressed: _captureFromCamera,
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                  child: const Icon(Icons.camera_alt, size: 36),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
