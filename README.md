# Third part of case study: Shopping Cart Analysis
# CASE STUDY: Tối ưu hóa chiến lược Marketing bằng Dual-Clustering & Association Rules 

## Thông tin nhóm
- **Nhóm:** 2
- **Thành viên:**
 - Đinh Hoài Nam
 - Đỗ Trung Kiên
 - Lưu Thế Hưng
- **Chủ đề:** Phân cụm khách hàng dựa trên luật kết hợp
- **Dataset:** Online Retail (UCI)

## Đặt vấn đề
Trong kinh doanh bán lẻ, thách thức lớn nhất không phải là thiếu dữ liệu, mà là làm sao để biến những dòng giao dịch khô khan thành chiến lược tăng trưởng. Dự án này triển khai một hướng tiếp cận hiện đại: Dual-Clustering (Phân cụm kép) kết hợp cùng Luật kết hợp (Association Rules) để tối ưu hóa đồng thời cả hành vi khách hàng và danh mục sản phẩm.
## Mục tiêu
Mục tiêu của dự án là xây dựng một hệ thống phân tích đa chiều: không chỉ hiểu Ai (Persona) là người mua hàng tiềm năng nhất thông qua RFM, mà còn biết Cái gì (Basket) nên được bán cùng nhau thông qua Association Rules để tối ưu hóa đồng thời cả tỷ lệ giữ chân (Retention) và giá trị đơn hàng (AOV).
## 1. Ý tưởng & Feynman Style

Giải thích đơn giản: Hãy tưởng tượng bạn là một chủ cửa hàng tạp hóa thông minh.

 - **Clustering** Giống như việc bạn nhận ra có một nhóm khách chuyên mua đồ cao cấp vào cuối tuần và một nhóm khách sinh viên chỉ mua đồ khuyến mãi. Bạn sẽ có cách chào mời khác nhau cho mỗi nhóm.
 - **Kết hợp** Bạn biết "Nhóm cao cấp" thường mua "Rượu vang" kèm "Phô mai", bạn sẽ tạo một Combo sang trọng dành riêng cho họ.

## 2. Quy trình thực hiện

1. Tiền xử lý dữ liệu giao dịch
2. Khai phá luật kết hợp bằng Apriori / Fp-Growth
3. Lựa chọn top-k luật làm đàu vào
4. Feature engineering từ luật kết hợp
5. Phân cụm khách hàng bằng K-means
6. Trực quán hóa và đánh giá cụm
7. Profiling cụm và đề xuất chiến lược marketting
8. Xây dựng dashboard streamlit.

## 3. Tiền xử lý dữ liệu

- Những bước làm sạch: 
 - Loại bỏ sản phẩm "rỗng"
 - Loại bỏ giao dịch bị hủy (InvoiceNo bắt đầu "C")
 - Loại bỏ số lượng âm

- Thống kê nhanh:
 - Số giao dịch sau lọc: 485,123 (United Kingdom)
 - Số sản phẩm: 4,007
 - Tổng số luật ban đầu: 3,856
 - Tổng số luật sau khi lọc: 1,794

## 4. Thực hiện các yêu cầu

**Lựa chọn luật kết hợp**
Để đảm bảo chất lượng đầu vào, nhóm đã thực hiện lọc luật nghiêm ngặt:
Thuật toán Apriori.
 - Ngưỡng lọc: min_support = 0.01
 - min_confidence = 0.3
 - min_lift = 1.2

Các luật được sắp xếp theo lift
Chỉ giữ lại Top-K luật có chất lượng cao để làm đặc trưng.

**Lý do:** 
 - Luật có lift cao phản ảnh mối liên hệ mạnh giữa các sản phẩm
 - Giảm nhiễu và tránh đặc trưng quá thưa cho bước phân cụm.

Bảng dưới đây được trích trực tiếp từ file rule output

| #  | Antecedents                               | Consequents          | Support  | Confidence | Lift      |
| -- | ----------------------------------------- | -------------------- | -------- | ---------- | --------- |
| 1  | HERB MARKER PARSLEY, HERB MARKER ROSEMARY | HERB MARKER THYME    | 0.010932 | 0.951691   | 74.567045 |
| 2  | HERB MARKER MINT, HERB MARKER THYME       | HERB MARKER ROSEMARY | 0.010932 | 0.951691   | 74.567045 |
| 3  | HERB MARKER MINT, HERB MARKER THYME       | HERB MARKER PARSLEY  | 0.010932 | 0.951691   | 74.567045 |
| 4  | HERB MARKER PARSLEY, HERB MARKER THYME    | HERB MARKER ROSEMARY | 0.010932 | 0.951691   | 74.567045 |
| 5  | HERB MARKER BASIL, HERB MARKER THYME      | HERB MARKER ROSEMARY | 0.010932 | 0.951691   | 74.567045 |
| 6  | HERB MARKER BASIL, HERB MARKER ROSEMARY   | HERB MARKER THYME    | 0.010932 | 0.951691   | 74.567045 |
| 7  | HERB MARKER MINT, HERB MARKER ROSEMARY    | HERB MARKER THYME    | 0.010932 | 0.951691   | 74.567045 |
| 8  | HERB MARKER CHIVES                        | HERB MARKER PARSLEY  | 0.010932 | 0.951691   | 74.567045 |
| 9  | HERB MARKER THYME, HERB MARKER PARSLEY    | HERB MARKER BASIL    | 0.010932 | 0.951691   | 74.567045 |
| 10 | HERB MARKER ROSEMARY, HERB MARKER BASIL   | HERB MARKER PARSLEY  | 0.010932 | 0.951691   | 74.567045 |

--> Các luật này được sử dụng làm đặc trưng đầu vào cho bước phân cụm khách hàng.

## 5. Feature Engineering cho Phân cụm

Nhóm xây dựng hai biến thể đặc trưng để so sánh.

- **Rule-based Binary (Baseline)**
 - Mỗi luật tương ứng với một chiều đặc trưng
 - Với mỗi khách hàng:
  - Gán 1 nếu khách hàng thỏa antecedent của luật
  - Gán 0 nếu không thỏa

Biến thể này phản ánh sự xuất hiện của hành vi mua kèm, đóng vai trò baseline cho so sánh.

- **Rule-based + RFM**
 - Sử dụng các luật kết hợp đã lọc
 - Ghép thêm RFM (Recency – Frequency – Monetary):
  - Recency: số ngày từ lần mua gần nhất
  - Frequency: số lần giao dịch
  - Monetary: tổng giá trị mua hàng
 - Các đặc trưng được chuẩn hóa (scale) trước khi đưa vào mô hình K-Means

## 5. Chọn số cụm K và huấn luyện mô hình 
Nhóm khảo sát K với Silhoutte score và thu được kết quả thực tế sau: 

| **K** | **Silhouette** |
| 2 |	0.875162 |
| 3 |	0.873354 |
| 12 |	0.442162 |
| 11 |	0.384972 |
| 9 |	0.371130 |
| 10 |	0.366702 |
| 5 |	0.295026 |
| 8 |	0.271498 |
| 7 |	0.265041 |
| 6 |	0.263301 |
| 4 |	0.126298 |

**Lựa chọn K**

- K = 2 cho silhouette cao nhất
- K = 3 được chọn vì:
 - Silhouette rất cao (0.873354), gần bằng K = 2
 - Tạo ra 3 nhóm khách hàng có ý nghĩa hành động rõ ràng hơn cho marketing
 - Tránh phân cụm quá thô như k = 2

## 6. Kết quả phân cụm và Profiling

**| Cluster |	Số khách hàng |	Recency |	Frequency	|  Monetary |**
| 0 |	3,797 |	93.22 |	4.05 |	1,809.82 |
| 1 |	123 |	61.02 |	10.31 |	3,548.75 |
| 2 |	1 |	1.00 |	1,373.00 |	1,716,831 |

- **Diễn giải cụm**
  - **Cluster 0 - Standard Mass – Khách Phổ thông rủi ro**
  - Persona: Khách vãng lai, chi tiêu thấp, Recency cao (93 ngày).
  - Chiến lược: Win-back Campaign - Tặng mã Freeship cho các món hàng từng xem để kích hoạt lại.

  - **Cluster 1 - Herb Enthusiasts – Người yêu Thảo mộc**
  - Persona: Persona: Khách trung thành, luôn mua theo bộ sưu tập làm vườn (Lift 74.5).
  - Chiến lược: Bundle Strategy - Đóng gói trọn bộ 6 nhãn thảo mộc hoặc tặng kèm hạt giống khi mua combo.

  - **Cluster 2 - Cluster 2 – Strategic Whale – Đối tác Chiến lược**
  - Persona: Khách sỉ cực lớn, mua hàng hàng ngày.
  - Chiến lược: Chăm sóc đặc quyền 1-1, chiết khấu sỉ theo bậc thang đơn hàng.
 
## 7. Trực quan hóa cụm


## 8. So sánh các biến thể đặc trưng
| Biến thể | Nhận xét |
| ----- | ----------------------------------------- |
| Rule-only | Phản ánh hành vi mua kèm nhưng thiếu thông tin giá trị |
| Rule + RFM | Cụm rõ ràng hơn, dễ diễn giải hơn cho marketing |
| Top-K nhỏ | Thiếu thông tin hành vi |
| Top-K = 200 | Cân bằng tốt giữa độ chi tiết và độ ổn định |

