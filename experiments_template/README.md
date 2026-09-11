# Thí nghiệm X.Y: [Tên Thí nghiệm] (Experiment Template)

> *Mẫu chuẩn 13 mục bắt buộc cho mọi bài thí nghiệm trong repository theo quy định tại `AGENTS.md`.*

---

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_XX_name`
- **Chương liên kết**: Chương XX — [Tên Chương]
- **Trạng thái**: 🚧 Chưa triển khai / 📖 Cần phần cứng / ✅ Đã kiểm chứng
- **Mục đích**: [Mô tả ngắn gọn 1-2 câu về mục tiêu kỹ thuật cần chứng minh]

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- [Giải thích tại sao thí nghiệm này cần thiết cho người học và đóng góp gì vào bài báo nghiên cứu]

## 3. Mục tiêu Phần cứng
- [NVIDIA Jetson Orin (Nano/NX/AGX) / AMD Xilinx Kria KV260 / ZCU104 / Mô phỏng CPU]

## 4. Dẫn xuất Toán học & Thuật toán
- [Trình bày công thức toán học, thuật toán hoặc sơ đồ luồng dữ liệu liên quan]

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- [Mô tả tập dữ liệu âm thanh, tần số lấy mẫu (16 kHz), định dạng PCM, độ dài khung]

## 6. Lệnh Thực thi
```bash
python chapterXX/exp_XX_name/run.py
pytest chapterXX/exp_XX_name/test_exp.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- [Chỉ số chấp nhận: ví dụ SQNR > 50 dB, MAE < 1e-4, WER drop < 0.3%]

## 8. Phương pháp Đo lường
- [Cách đo thời gian, bộ đếm chu kỳ clock, công cụ đo công suất tegrastats hoặc XPE]

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Bảng số liệu thực tế đo được sau khi chạy trên phần cứng]

## 10. Đánh đổi Phần cứng - Phần mềm
- [Phân tích sự đánh đổi giữa tài nguyên phần cứng (LUTs/DSPs) và độ trễ / độ chính xác]

## 11. Giới hạn & Giả định
- [Các giả định đơn giản hóa hoặc điều kiện biên chưa bao quát]

## 12. Bài học Sư phạm Rút ra
- [1-3 bài học cốt lõi người đọc cần ghi nhớ]

## 13. Nguồn Trích dẫn
- [Mã nguồn tham chiếu từ `docs/source_index.json`, ví dụ `R01-01`, `R01-04`]
