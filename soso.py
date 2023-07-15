# def merge_pdf(list_pdf):

#     merger = PdfWriter()
#     # 列出你要合并的PDF文件名和要删除的页面
#     pdf_files = [
#         {"filename": "file1.pdf", "pages_to_delete": [2, 3]},
#         {"filename": "file2.pdf", "pages_to_delete": []},
#         {"filename": "file3.pdf", "pages_to_delete": [1]}
#     ]

#     # 遍历每个PDF文件
#     for pdf_file in pdf_files:
#         # 打开PDF文件
#         input_pdf = PdfWriter(open(pdf_file["filename"], "rb"))
        
#         # 遍历PDF中的每一页
#         for i in range(input_pdf.getNumPages()):
#             # 如果当前页不在要删除的页面列表中，则添加到输出PDF中
#             if i not in pdf_file["pages_to_delete"]:
#                 merger.addPage(input_pdf.getPage(i))

#     # 将合并后的PDF写入新的文件
#     with open("merged.pdf", "wb") as merger_pdf:
#         merger.write(merger_pdf)