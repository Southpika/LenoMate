import pptx
import pdfplumber

class read_file():
    def __init__(self,location):
        if location.endswith('.pptx') or location.endswith('.ppt'):
            self.mode = 'ppt'
            self.slides = pptx.Presentation(location).slides
        if location.endswith('.pdf'):
            self.mode = 'pdf'
            self.path = location
    
    def fit(self,trucation=0,verbose=False):
        if self.mode == 'ppt':
            content = ''
            start = 0
            
            for slide in self.slides:
                start += 1
                temp_content = ''
                for shape in slide.shapes:               
                    if not shape.has_text_frame:
                        continue
                    text_frame = shape.text_frame
                    
                    for paragraph in text_frame.paragraphs:
                        
                        temp_content += paragraph.text + ' '
                    if verbose:
                        print('temp',temp_content)

                if len(temp_content) > trucation:
                    content += f"第{start}页："             
                    content += temp_content
                    content += '\n'
                    if verbose:
                        print('---------------------')
            return content
        elif self.mode == 'pdf':
            with pdfplumber.open(self.path) as pdf: 
                content = ''
                for i in range(len(pdf.pages)):
                    # 读取PDF文档第i+1页
                    page = pdf.pages[i] 
                    # page.extract_text()函数即读取文本内容，下面这步是去掉文档最下面的页码
                    page_content = '\n'.join(page.extract_text().split('\n')[:-1])
                    content = content + page_content
            return content

if __name__ == '__main__':
    location = input('location:')
    read_file = read_file(location)
    print(read_file.fit(trucation=10))