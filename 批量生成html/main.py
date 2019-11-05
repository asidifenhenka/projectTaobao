# coding=utf8
# by asdfhk
import zipfile
import requests
import xlrd
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib import request
import shutil   #文件处理模块
import re
import os
from pydocx import PyDocX  #word文件处理模块


class Data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Refer': 'https://www.toutiao.com/'
    }
    data = {}

    def get_url(self, url):
        try:
            response = requests.get(url, headers=Data.headers)
            # print(response.status_code)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # self.get_text(soup)
                return soup

        except RequestException:
            print('文章链接错误或没有找到文章链接', url)

    def get_text(self, soup):
        # global data
        titles = soup.find_all('title')
        for a in titles:
            title = a.get_text()
        contents = soup.find_all('script')
        content = list(contents[6].stripped_strings)
        for j in content:
            # print(j)
            content_data = re.search("u003.*E&quot;", j, re.DOTALL)

            content_data_str = str("\\" + content_data.group())
            # print(content_data_str)
            a = re.sub(r'(\\u[\s\S]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                       content_data_str)
            a = re.sub(r'&#x3D;\\&quot;', '=', a)
            a = re.sub(r'\\&quot;', '', a)
            # print(a)
            delete_text = re.findall(r'(<h1>关联阅读：</h1>.*)</div>',a,re.DOTALL)
            # print(delete_text)
            if delete_text:
                a = re.sub(delete_text[0],'',a)
                data = {
                    'b_text': a,
                    'a_title': title,
                    'code': 200
                }
            else:
                data = {
                    'b_text': a,
                    'a_title': title,
                    'code': 200
                }
            return data


class ExcleRead():
    def __init__(self):
        self.root_path = 'E:\projectTaobao' #存放项目的主目录
        self.excle_path = 'E:\projectTaobao\批量生成html\excle\data.xlsx'

    def read_excle(self):
        '''
        提供read_excle方法
        :return: excle里面每一行的信息
        '''
        list_dict = []
        excle = xlrd.open_workbook(self.excle_path)
        table = excle.sheet_by_name('Sheet1')
        rows = table.nrows  # 获取总行数
        for i in range(1,rows):

            titles_values = table.row_values(0)
            rows_values = table.row_values(int(i))
            dict_values = dict(zip(titles_values, rows_values))  # 组合成字典

            list_dict.append(dict_values) #存到列表
        return list_dict

    def get_article_forUrl(self,values):
        '''

        :return:文章主体
        '''

        getData = Data()
        # dict_values = self.read_excle()
        dict_values = values
        try:
            if dict_values['文章来源'] == 'url':
                print(dict_values['文章路径'])
                text  = getData.get_url(dict_values['文章路径'])
                article = getData.get_text(text)
                # print(article)
                return article['b_text']
        except:
            print('url错误或没有找到url',values)


    def get_article_forWord(self,values):
        path = self.root_path + '\批量生成html\word'
        os.chdir(path)
        html = PyDocX.to_html(values['文章文件名'])

        article = re.search(r'<p>.*</p>',html)
        artivle_final = '<div class="bbs_txt" style="text-indent:2em;line-height:2em;">' + article.group() + '</div>'
        # print(artivle_final)
        html_path = values['html文件路径'] + '\\' + values['html模板文件名']
        source_file = open(html_path, "r", encoding="utf-8")
        template_html = source_file.read()
        final_html = re.sub(r'<div class="bbs_txt" style="text-indent:2em;line-height:2em;"></div>',artivle_final,template_html)
        # print(final_html)
        f = open(values['生成html文件名'], 'w', encoding="utf-8")
        f.write(final_html)
        f.close()
        source_file.close()
        old_path = path + '\\' + values['生成html文件名']
        file_path = self.root_path + '\批量生成html\HtmlFiles'
        shutil.move(old_path, file_path)


    def word_picture(self,values):
        os.chdir(values['文章路径'])
        dirlist = os.listdir(values['文章路径'])
        for i in dirlist:
            if i.endswith(".docx"):  # 匹配docx文件
                docname = i.split(".")  # 以“.”做成列表形式
                os.rename(i, "%s.ZIP" % docname[0])  # 重命名为ZIP格式
                f = zipfile.ZipFile("%s.ZIP" % docname[0], 'r')
                for file in f.namelist():
                    if "word" in file:
                        f.extract(file)  # 将压缩包里的word文件夹解压出来
                f.close()
                oldimagedir = r"%s\word\media" % values['文章路径']  # 定义图片文件夹
                shutil.copytree(oldimagedir, "%s\%s" % (self.root_path + '\批量生成html\images', docname[0]))  # 拷贝到新目录，名称为word文件的名字
                os.rename("%s.ZIP" % docname[0], "%s.docx" % docname[0])  # 将ZIP名字还原为DOCX
                shutil.rmtree("%s\word" % values['文章路径'])  # 删除word文件夹


    def download_picture(self,values):
        '''
        提供download_picture方法
        :param values: read_excle返回的文件信息
        :return: 下载该文章的图片
        '''
        list_suffix = []
        article = self.get_article_forUrl(values)
        srcs = re.findall(r'<img src=(.*?) .*?>', article, re.DOTALL)
        path = self.root_path + '\批量生成html\images' + '\\' + values['图片前缀'] + '\\'

        if not os.path.exists(path):  #如果没有该文件夹 则创建
            os.makedirs(path)
        for src in srcs:
            suffix = src.split('/')
            list_suffix.append(suffix[-1])
            img_name = values['图片前缀'] + suffix[-1] + '.jpg'
            # print(img_name)
            request.urlretrieve(src, path+img_name)

    def article_sub(self,values,article):
        '''
        提供article_sub方法  对获取到的文章去除多于文本并插入图片的相对路径
        :param values:  read_excle返回的文件信息
        :param article: get_article_forUrl返回的文章主体
        :return: 处理好的文章主体
        '''
        os.chdir(self.root_path + '\批量生成html')
        list_imgpaths = []
        path = self.root_path + '\批量生成html\images' + '\\' + values['图片前缀'] + '\\'
        listdir_imgs = os.listdir(path)
        # print(listdir_imgs)
        abspath = os.getcwd()  # 获取当前路径
        # print(abspath)
        rootpath = os.path.abspath('..')  # 获取上级路径
        # print(rootpath)
        for listdir_img in listdir_imgs:
            img_path = '..'+'\\'+ 'images' + '\\'+values['图片前缀']+'\\'+listdir_img
            list_imgpaths.append(img_path)
            #获取图片的相对路径
        # print(list_imgpaths)
        cut_other = re.sub('&quot;','',article)  #去除多余文本
        cut_other = re.sub('<div>','',cut_other)
        cut_other = re.sub('</div>', '', cut_other)
        for list_imgpath in list_imgpaths:
            id_img = re.findall('%s(\w[A-Za-z0-9].*)\.' %values['图片前缀'], list_imgpath) #获取图片ID
            print(id_img)
            # sub_img = re.sub(r'http://p[0-9]\.pstatp\.com/\w/%s' % id_img[0],
            #                 list_imgpath, cut_other)
            # 根据图片ID插入对应图片相对路径  不改变原格式
            sub_img = re.sub(r'http://p[0-9]\.pstatp\.com/[\w\/\-]+/%s' % id_img[0],
                             list_imgpath, cut_other)
            cut_other = sub_img
        return sub_img


    def file_copy(self,values,article_final):
        # file_path = 'E:\projectTaobao\批量生成html\HtmlFiles'
        article = '<div class="bbs_txt" style="text-indent:2em;line-height:2em;">' + article_final + '</div>'
        file_path = self.root_path + '\批量生成html\HtmlFiles'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        html_path = values['html文件路径'] +'\\' + values['html模板文件名']
        source_file = open(html_path, "r", encoding="utf-8")
        # os.chdir(file_path)
        get_file = open(values['生成html文件名'], "a", encoding="utf-8")
        old_path = self.root_path + '\批量生成html' + '\\' + values['生成html文件名']
        template_html = source_file.read()
        final_html = re.sub(r'<div class="bbs_txt" style="text-indent:2em;line-height:2em;"></div>', article,
                            template_html)
        get_file.write(final_html)
        source_file.close()
        get_file.close()
        shutil.move(old_path, file_path)



def main():
    test = ExcleRead()
    values = test.read_excle()
    for value in values:
        if value['文章来源'] == 'url':
            print('开始生成',value['文章路径'])
            article_initial = test.get_article_forUrl(value)  #初始的文章
            print('开始下载图片')
            test.download_picture(value)    #下载图片
            article_final = test.article_sub(value,article_initial)   #拼接好的文章
            test.file_copy(value,article_final)
            print('成功生成 %s！'%value['生成html文件名'])
        elif value['文章来源'] == 'word':
            print('开始生成',value['文章路径'])
            test.get_article_forWord(value)
            test.word_picture(value)
            print('成功！')






if __name__ == '__main__':
    main()
