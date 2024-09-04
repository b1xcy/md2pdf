import base64

import markdown
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup, Tag, Doctype, NavigableString
import os


def convert_md2html(md_content: str) -> str:
    html_content: str = markdown.markdown(md_content,
                                          extensions=['extra', 'fenced_code', 'tables'])
    soup = BeautifulSoup(html_content, 'lxml')
    soup.insert(0, Doctype("html"))
    if not soup.head:
        head = soup.new_tag('head')
        soup.html.insert(0, head)
    else:
        head = soup.head
    head.append(soup.new_tag('meta', charset='UTF-8'))
    head.append(Tag(builder=soup.builder,
                    name='meta',
                    attrs={'name': 'viewport', 'content': 'width=device-width initial-scale=1'}))
    head.append(soup.new_tag('link', **{
        'rel': 'stylesheet',
        'href': 'main.css'
    }))
    return str(soup)


def prettify_html_body(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'lxml')
    body_tag = soup.body
    if body_tag:
        # body 新增 class="typora-export os-windows"
        body_tag['class'] = body_tag.get('class', []) + ['typora-export', 'os-windows']

        typora_export_content_div = soup.new_tag('div', **{'class': 'typora-export-content'})
        write_div = soup.new_tag('div', **{'id': 'write', 'class': ''})

        for child in list(body_tag.children):
            write_div.append(child)
        typora_export_content_div.append(write_div)
        body_tag.clear()
        body_tag.append(typora_export_content_div)
    return str(soup)


def prettify_html_pre_code(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'lxml')
    for pre_tag in soup.find_all('pre'):
        code_tag = pre_tag.find('code')
        if code_tag:
            code_content = code_tag.text
            # 创建最外层 pre
            new_pre = soup.new_tag('pre', **{
                'class': 'md-fences md-end-block ty-contain-cm modeLoaded',
                'spellcheck': 'false',
                'lang': ''
            })
            # 内层 div
            new_div = soup.new_tag('div', **{
                'class': 'CodeMirror cm-s-inner cm-s-null-scroll CodeMirror-wrap',
                'lang': ''
            })
            # 构造第一个嵌套 div
            first_div = soup.new_tag('div', **{
                'style': 'overflow: hidden; position: relative; width: 3px; height: 0px; top: 9.51562px; left: 8px;'
            })
            first_div.append(soup.new_tag('textarea', **{
                'autocorrect': 'off',
                'autocapitalize': 'off',
                'spellcheck': 'false',
                'tabindex': '0',
                'style': 'position: absolute; bottom: -1em; padding: 0px; width: 1000px; height: 1em; outline: none;'
            }))

            new_div.append(first_div)

            new_div.append(soup.new_tag('div', **{'class': 'CodeMirror-scrollbar-filler', 'cm-not-content': 'true'}))
            new_div.append(soup.new_tag('div', **{'class': 'CodeMirror-gutter-filler', 'cm-not-content': 'true'}))

            # 构造第二个嵌套 div CodeMirror-scroll
            second_div = soup.new_tag('div', **{
                'class': 'CodeMirror-scroll',
                'tabindex': '-1'
            })
            # CodeMirror-scroll的内层嵌套
            tag_CodeMirror_sizer = soup.new_tag('div', **{
                'class': 'CodeMirror-sizer',
                'style': 'margin-left: 0px; margin-bottom: 0px; border-right-width: 0px; padding-right: 0px; '
                         'padding-bottom: 0px;'})
            tag_position = soup.new_tag('div', **{
                'style': 'position: relative; top: 0px;'
            })
            tag_CodeMirror_lines = soup.new_tag('div', **{
                'class': 'CodeMirror-lines',
                'role': 'presentation'
            })
            tag_presentation = soup.new_tag('div', **{
                'role': 'presentation',
                'style': 'position: relative; outline: none;'
            })
            tag_presentation.append(soup.new_tag('div', **{
                'class': 'CodeMirror-measure'
            }))
            tag_presentation.append(soup.new_tag('div', **{
                'class': 'CodeMirror-measure'
            }))
            tag_presentation.append(soup.new_tag('div', **{
                'style': 'position: relative; z-index: 1;'
            }))
            tag_CodeMirror_code = soup.new_tag('div', **{
                'class': 'CodeMirror-code',
                'role': 'presentation'
            })
            tag_CodeMirror_activeline = soup.new_tag('div', **{
                'class': 'CodeMirror-activeline',
                'style': 'position: relative;'
            })
            tag_CodeMirror_activeline.append(soup.new_tag('div', **{
                'class': 'CodeMirror-activeline-background CodeMirror-linebackground'
            }))
            tag_CodeMirror_activeline.append(soup.new_tag('div', **{
                'class': 'CodeMirror-gutter-background CodeMirror-activeline-gutter',
                'style': 'left: 0px; width: 0px;'
            }))
            tag_pre_CodeMirror_line = soup.new_tag('pre', **{
                'class': ' CodeMirror-line ',
                'role': 'presentation'
            })
            tag_pre_CodeMirror_line.append(soup.new_tag('span', **{
                'style': 'padding-right: 0.1px;',
                'class': 'presentation'
            }))
            tag_pre_CodeMirror_line.span.append(NavigableString(code_content))

            # 整理children顺序
            tag_CodeMirror_activeline.append(tag_pre_CodeMirror_line)
            tag_CodeMirror_code.append(tag_CodeMirror_activeline)
            tag_presentation.append(tag_CodeMirror_code)
            tag_CodeMirror_lines.append(tag_presentation)
            tag_position.append(tag_CodeMirror_lines)
            tag_CodeMirror_sizer.append(tag_position)
            second_div.append(tag_CodeMirror_sizer)
            second_div.append(
                soup.new_tag('div', **{
                    'style': 'position: absolute; height: 0px; width: 1px; border-bottom: 0px solid transparent; top: '
                             '23px;'
                })
            )
            second_div.append(soup.new_tag('div', **{
                'class': 'CodeMirror-gutters',
                'style': 'display: none; height: 23px;'
            }))
            new_div.append(second_div)
            new_pre.append(new_div)
            pre_tag.replace_with(new_pre)
    return str(soup)


def prettify_html_dot(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'lxml')
    for li_tag in soup.find_all('li'):
        new_li_content = ''.join(str(item).strip() for item in li_tag.contents)
        li_tag.clear()
        li_tag.append(BeautifulSoup(new_li_content, 'lxml'))
    return str(soup)


def convert_html2pdf(html_path: str) -> dict:
    work_path = os.getcwd() + "\\"
    edge_options = Options()
    edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')

    edge_options.add_argument('--print-to-pdf-no-header')
    edge_options.add_argument('--kiosk-printing')

    driver = webdriver.Edge(options=edge_options)

    driver.get("file://" + work_path + html_path)
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
        'printBackground': True,
        'displayHeaderFooter': False,
        'preferCSSPageSize': True
    })
    driver.quit()
    return pdf_data


with open('test.md', 'r', encoding='utf-8') as md_file:
    md_content = md_file.read()

html_content = convert_md2html(md_content)
modify_html = prettify_html_dot(prettify_html_pre_code(prettify_html_body(html_content)))
with open('test.html', 'w', encoding='utf-8') as html:
    html.write(modify_html)

try:
    with open("test.pdf", "wb") as file:
        pdf_data_base64 = convert_html2pdf("test.html")['data']
        pdf_raw = base64.b64decode(pdf_data_base64)
        file.write(pdf_raw)
except Exception as e:
    print(e)
