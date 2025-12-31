# CHƯƠNG 1. GIỚI THIỆU ĐỀ TÀI

## 1.1 Đặt vấn đề

Trong bối cảnh chuyển đổi số toàn cầu, giáo dục là một trong những lĩnh vực đang chịu tác động mạnh mẽ từ sự phát triển của trí tuệ nhân tạo (AI). Theo báo cáo của UNESCO năm 2023, hơn 60% các cơ sở giáo dục trên thế giới đang tìm kiếm giải pháp ứng dụng AI để nâng cao hiệu quả giảng dạy và học tập. Tại Việt Nam, nhu cầu này càng trở nên cấp thiết khi số lượng giáo viên, sinh viên và nhân viên văn phòng cần xử lý khối lượng tài liệu lớn ngày càng tăng.

Việc soạn thảo bài giảng, tạo slide trình bày và biên soạn bài kiểm tra trắc nghiệm là những công việc tốn nhiều thời gian và công sức của giáo viên. Một giáo viên trung bình có thể mất từ 2-4 giờ để tạo một bộ slide bài giảng hoàn chỉnh từ tài liệu có sẵn, và thêm 1-2 giờ để biên soạn bộ câu hỏi trắc nghiệm tương ứng. Khi nhân với số lượng bài giảng trong một học kỳ, thời gian này trở thành gánh nặng đáng kể, ảnh hưởng đến chất lượng giảng dạy và nghiên cứu.

Hiện nay, nhiều công cụ AI như ChatGPT, Google Gemini, Gamma.app đã ra đời để hỗ trợ các tác vụ này. Tuy nhiên, các công cụ này đều hoạt động trên nền tảng đám mây (cloud-based), dẫn đến một số thách thức nghiêm trọng trong môi trường giáo dục Việt Nam. Thứ nhất, vấn đề bảo mật dữ liệu khi tài liệu giảng dạy, đề thi, bài kiểm tra là tài sản trí tuệ quan trọng của giáo viên và nhà trường. Thứ hai, chi phí sử dụng các dịch vụ AI thương mại cao, không phù hợp với ngân sách giáo dục còn hạn chế. Thứ ba, nhiều cơ sở giáo dục ở vùng sâu, vùng xa có kết nối Internet không ổn định, khiến việc sử dụng dịch vụ đám mây trở nên khó khăn.

Xuất phát từ thực tế trên, việc xây dựng một hệ thống AI có khả năng hoạt động hoàn toàn nội bộ (on-premise), đảm bảo bảo mật dữ liệu và không phụ thuộc kết nối Internet là một nhu cầu thiết thực. Nếu vấn đề này được giải quyết, giáo viên và người dùng có thể tiết kiệm đáng kể thời gian soạn bài, đồng thời đảm bảo an toàn cho dữ liệu giáo dục nhạy cảm. Giải pháp này không chỉ áp dụng trong lĩnh vực giáo dục mà còn có thể mở rộng sang các lĩnh vực khác như doanh nghiệp, tổ chức chính phủ nơi yêu cầu cao về bảo mật thông tin.

## 1.2 Mục tiêu và phạm vi đề tài

Hiện nay, các giải pháp hỗ trợ phân tích tài liệu và tạo nội dung tự động trên thị trường có thể chia thành hai nhóm chính. Nhóm thứ nhất là các chatbot AI đa năng như ChatGPT, Google Gemini, Claude. Các công cụ này có khả năng xử lý ngôn ngữ tự nhiên mạnh mẽ, hỗ trợ phân tích tài liệu và trả lời câu hỏi. Tuy nhiên, chúng không thể tạo file slide PowerPoint trực tiếp, chi phí sử dụng cao (ChatGPT Plus: $20/tháng), và dữ liệu được gửi lên máy chủ cloud, tiềm ẩn rủi ro bảo mật. Nhóm thứ hai là các công cụ tạo slide chuyên biệt như Gamma.app, Beautiful.ai, Canva AI. Các công cụ này tạo slide với giao diện đẹp mắt và nhiều template chuyên nghiệp. Tuy nhiên, chúng không có khả năng phân tích tài liệu đầu vào, không hỗ trợ hỏi đáp với nội dung, chi phí cao (Gamma Pro: $15/tháng), và hoàn toàn phụ thuộc vào kết nối Internet.

Qua so sánh, có thể nhận thấy các hạn chế chung của các giải pháp hiện tại bao gồm: (i) không thể triển khai nội bộ (on-premise) để đảm bảo bảo mật, (ii) không tích hợp đầy đủ các chức năng phân tích tài liệu, tạo slide và tạo quiz trong một hệ thống, (iii) chi phí vận hành cao do phụ thuộc vào API trả phí, và (iv) khả năng tùy chỉnh hạn chế, đặc biệt về mặt mô hình AI và ngôn ngữ.

Trên cơ sở đó, đồ án này hướng tới mục tiêu xây dựng một hệ thống phân tích tài liệu và tạo slide thông minh có tên **AI NVCB** với các chức năng chính sau. Thứ nhất, phân tích tài liệu đa định dạng bao gồm PDF, DOCX, TXT, MD với khả năng tóm tắt nội dung và hỏi đáp thông minh dựa trên kỹ thuật RAG (Retrieval-Augmented Generation). Thứ hai, tạo slide tự động từ chủ đề hoặc tài liệu đầu vào, xuất file PowerPoint (PPTX) có thể chỉnh sửa. Thứ ba, tạo bài trắc nghiệm tự động với câu hỏi và đáp án từ nội dung tài liệu. Thứ tư, quản lý mô hình AI linh hoạt, cho phép người dùng thay đổi mô hình ngôn ngữ lớn (LLM) phù hợp với nhu cầu và cấu hình phần cứng.

Phạm vi của đề tài giới hạn trong việc xây dựng hệ thống ứng dụng web hoạt động trên máy chủ nội bộ, sử dụng Ollama làm nền tảng chạy LLM cục bộ. Hệ thống được tối ưu cho ngôn ngữ tiếng Việt và hướng đến đối tượng người dùng chính là giáo viên, sinh viên và nhân viên văn phòng.

## 1.3 Định hướng giải pháp

Để giải quyết các vấn đề đã nêu, đồ án lựa chọn hướng tiếp cận xây dựng nền tảng AI on-premise, sử dụng các công nghệ mã nguồn mở và mô hình ngôn ngữ lớn chạy cục bộ.

Về công nghệ AI, đồ án sử dụng **Ollama** làm LLM server cho phép chạy các mô hình ngôn ngữ lớn như Qwen2.5, Llama 3, Gemma 2 trực tiếp trên máy tính. Kết hợp với **LangChain** làm framework điều phối, hệ thống triển khai pipeline RAG (Retrieval-Augmented Generation) để hỏi đáp dựa trên ngữ cảnh tài liệu. Vector database **FAISS** được sử dụng để lưu trữ và tìm kiếm ngữ nghĩa trên embedding của tài liệu.

Về kiến trúc hệ thống, đồ án áp dụng kiến trúc phân lớp (Layered Architecture) với bốn tầng chính: tầng trình bày (Streamlit), tầng API (FastAPI), tầng nghiệp vụ (Document Service, Slide Service, Model Manager), và tầng truy cập dữ liệu (Repository Pattern với SQLite). Kiến trúc này đảm bảo tính module hóa, dễ bảo trì và mở rộng.

Giải pháp của đồ án là hệ thống AI NVCB - một nền tảng tích hợp cho phép: (i) upload và phân tích tài liệu đa định dạng, (ii) tóm tắt nội dung và hỏi đáp với RAG, (iii) tự động sinh slide PowerPoint với nội dung từ LLM, (iv) tạo câu hỏi trắc nghiệm từ tài liệu, và (v) quản lý linh hoạt các mô hình AI với khả năng hot-swap không cần khởi động lại hệ thống.

Đóng góp chính của đồ án bao gồm sáu điểm nổi bật. Thứ nhất, xây dựng thành công nền tảng AI on-premise hoàn toàn hoạt động offline, đảm bảo bảo mật dữ liệu 100%. Thứ hai, thiết kế pipeline RAG tối ưu cho tiếng Việt với chiến lược chunking và truy xuất theo chủ đề, đạt F1-Score 84% trên bộ test nội bộ. Thứ ba, phát triển hệ thống quản lý LLM linh hoạt với Singleton Pattern, cho phép chuyển đổi mô hình trong thời gian dưới 2 giây. Thứ tư, giải quyết vấn đề xử lý tiếng Việt với LLM đa ngôn ngữ thông qua bộ lọc ký tự và prompt engineering, đạt tỷ lệ output thuần Việt 99.5%. Thứ năm, triển khai cơ chế structured generation với logic retry, đạt tỷ lệ parse JSON thành công 99%. Thứ sáu, thiết kế hệ thống sẵn sàng production với Docker multi-stage build, giảm 68% kích thước image và tích hợp health monitoring.

## 1.4 Bố cục đồ án

Phần còn lại của báo cáo đồ án tốt nghiệp này được tổ chức như sau.

Chương 2 trình bày quá trình khảo sát hiện trạng và phân tích yêu cầu cho hệ thống AI NVCB. Nội dung chương bao gồm khảo sát các sản phẩm tương tự trên thị trường, xây dựng biểu đồ use case tổng quát và phân rã cho từng chức năng chính, đặc tả chi tiết các use case quan trọng, cùng các yêu cầu phi chức năng về hiệu năng, bảo mật và khả năng bảo trì của hệ thống.

Trong Chương 3, em trình bày các công nghệ và nền tảng được sử dụng trong quá trình phát triển hệ thống. Chương này phân tích các lựa chọn công nghệ cho từng thành phần: Ollama và LangChain cho xử lý ngôn ngữ tự nhiên, FastAPI cho backend API, Streamlit cho giao diện người dùng, FAISS cho vector database, python-pptx cho tạo file PowerPoint, cùng Docker và Nginx cho triển khai production. Với mỗi công nghệ, lý do lựa chọn được giải thích dựa trên các yêu cầu đã xác định tại Chương 2.

Chương 4 trình bày chi tiết thiết kế, triển khai và đánh giá hệ thống. Về thiết kế, chương mô tả kiến trúc phân lớp với biểu đồ gói UML, thiết kế chi tiết giao diện người dùng, biểu đồ lớp cho các service chính, và cơ sở dữ liệu SQLite. Về triển khai, chương trình bày môi trường phát triển, các API endpoint, và quy trình Docker hóa. Về đánh giá, chương đưa ra kết quả kiểm thử chức năng, phi chức năng và các hình ảnh demo hệ thống.

Chương 5 trình bày đóng góp chính của đồ án, bao gồm sáu giải pháp kỹ thuật nổi bật. Thứ nhất là giải pháp nền tảng AI on-premise cho phép hoạt động hoàn toàn offline với Ollama. Thứ hai là pipeline RAG đa tài liệu với truy xuất theo chủ đề, tối ưu cho tiếng Việt. Thứ ba là hệ thống quản lý LLM linh hoạt với cơ chế hot-swapping. Thứ tư là bộ giải pháp xử lý ngôn ngữ Việt với LLM đa ngôn ngữ. Thứ năm là cơ chế structured generation với JSON parsing robust. Thứ sáu là thiết kế production-ready với Docker và health monitoring. Với mỗi giải pháp, chương trình bày vấn đề, giải pháp đề xuất và kết quả đạt được.

Chương 6 trình bày kết luận và hướng phát triển của đồ án. Phần kết luận so sánh hệ thống với các sản phẩm tương tự, tổng kết các chức năng đã hoàn thành, các chỉ tiêu đạt được, những hạn chế còn tồn tại và bài học kinh nghiệm. Phần hướng phát triển đề xuất các công việc hoàn thiện trong ngắn hạn, các tính năng mới trong trung và dài hạn, cùng định hướng nghiên cứu tiềm năng.
