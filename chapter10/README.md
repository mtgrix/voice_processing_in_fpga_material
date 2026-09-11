# Thí nghiệm 10.1: Đánh giá Đa mục tiêu & Dựng Đồ thị Pareto Frontier (Pareto Evaluation)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_10_pareto_frontier_eval`
- **Chương liên kết**: Chương 10 — Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo Khoa học
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Tổng hợp toàn bộ dữ liệu đo kiểm từ Jetson Orin và FPGA Kit để tự động vẽ biểu đồ Pareto Frontier 2D/3D (Độ trễ vs Năng lượng vs Độ chính xác), phục vụ trực tiếp cho phần Experimental Results của bài báo khoa học.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Nắm vững cách phân tích dữ liệu thực nghiệm và trực quan hóa kết quả theo chuẩn mực của các bài báo IEEE/ACM.

## 3. Mục tiêu Phần cứng
- Dữ liệu thực nghiệm thu thập từ NVIDIA Jetson Orin và AMD Xilinx Kria KV260.

## 4. Dẫn xuất Toán học & Thuật toán
- Định nghĩa tập tối ưu Pareto: Điểm $x$ trội hơn $y$ nếu $x$ không kém $y$ trên mọi tiêu chí và vượt trội hơn trên ít nhất một tiêu chí.
- Chỉ số Energy-Delay Product (EDP).

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Bảng log kết quả đo đạc từ các bài thí nghiệm `exp_02` đến `exp_09`.

## 6. Lệnh Thực thi
```bash
python chapter10/exp_10_pareto_frontier_eval/plot_pareto.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Biểu đồ xuất ra định dạng vector PDF/SVG chất lượng cao sẵn sàng đưa vào LaTeX bài báo.

## 8. Phương pháp Đo lường
- Tổng hợp số liệu qua thư viện Pandas và Matplotlib/Seaborn.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ nạp toàn bộ số liệu thực nghiệm hoàn chỉnh]

## 10. Đánh đổi Phần cứng - Phần mềm
- Minh chứng trực quan vùng biên nơi FPGA vượt trội về năng lượng ở các mức độ trễ khắt khe.

## 11. Giới hạn & Giả định
- Các điểm đo phải được thu thập dưới cùng một kịch bản âm thanh thử nghiệm.

## 12. Bài học Sư phạm Rút ra
- Trong nghiên cứu khoa học, một biểu đồ Pareto chuẩn xác có giá trị thuyết phục hơn hàng ngàn lời diễn giải định tính.

## 13. Nguồn Trích dẫn
- `R01-01`, `R01-02`, `R01-04`.
