import argparse
from ebooklib import epub
from bs4 import BeautifulSoup
import os

def bold_first_half(word):
    halfway_index = len(word) // 2 
    formatted_word = f'<span style="font-weight: bold;">{word[:halfway_index]}</span>{word[halfway_index:]}'
    return formatted_word

def modify_epub(input_epub_path, output_epub_path):
    book = epub.read_epub(input_epub_path)
    modified_book = epub.EpubBook()

    spine_items = {}  # Store spine items with idref as key

    for spine_item_id, idref in book.spine:
        spine_item = book.get_item_with_id(spine_item_id)
        if isinstance(spine_item, epub.EpubHtml):
            content = spine_item.content.decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            # Add <style> tag to the <head> section
            head = soup.new_tag("head")
            style = soup.new_tag("style")
            style.append(".half-bold { font-weight: bold; }")
            head.append(style)
            soup.head.replace_with(head)

            for p_tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                p_tag.append("###")

            for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                words = tag.get_text().split()
                formatted_words = [bold_first_half(word) for word in words]
                modified_content = ' '.join(formatted_words)
                tag.clear()
                tag.append(BeautifulSoup(modified_content, 'html.parser'))

            # Add "#" at the end of every <p> tag



            modified_content = str(soup)

            # Replace <span style="font-weight: bold;">#lt;</span>/p&gt; with <br> in modified_content
            modified_content = modified_content.replace('###', '<br/><br/>')
            modified_content = modified_content.replace('#</span>##', '</span><br/>')

            modified_content = modified_content.encode('utf-8')
            modified_item = epub.EpubHtml(title=spine_item.title, file_name=spine_item.file_name, lang='en', content=modified_content)
            modified_book.add_item(modified_item)




            spine_items[spine_item_id] = modified_item  # Store the modified item with id as key

    # Construct the modified spine using the stored items
    for spine_item_id, idref in book.spine:
        if spine_item_id in spine_items:
            modified_book.spine.append((spine_items[spine_item_id], idref))

    # Set metadata for the modified book
    modified_book.set_title(book.get_metadata('DC', 'title')[0][0])
    modified_book.set_language(book.get_metadata('DC', 'language')[0][0])

    epub.write_epub(output_epub_path, modified_book)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Modify an EPUB file to bold the first half of each word in content.')
    parser.add_argument('input_epub', help='Path to the input EPUB file')
    args = parser.parse_args()

    output_file_name = os.path.splitext(os.path.basename(args.input_epub))[0] + "_halfbolded.epub"
    output_epub_path = os.path.join(os.path.dirname(args.input_epub), output_file_name)

    modify_epub(args.input_epub, output_epub_path)
