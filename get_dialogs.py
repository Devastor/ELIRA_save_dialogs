from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import pickle
import argparse
import random

_TITLE_ = "Devastor_ELIRA_dialogue"
FONT_NAME = "KazmannSans"
FONT_FILENAME = FONT_NAME + ".ttf"
GLOBAL_PAGES = 1
dialogue = []
# Устанавливаем шрифт
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILENAME))

def read_config(file_path):
    """Чтение параметров из файла конфигурации."""
    params = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value
    return params

def create_pdf(dialogue_lines, output_file=_TITLE_, current_width=945, current_height=945,
              marginX=0, marginY=0, offset=0, font_size=1, font_name=FONT_NAME):
    global GLOBAL_PAGES
    current_width = int(current_width)
    current_height = int(current_height)
    marginX = int(marginX)
    marginY = int(marginY)
    offset = int(offset)
    font_size = int(font_size)
    current_y = current_height - marginY
    current_file_size = 0
    symbols_in_PDF = 0
    CANVASES = []
    CANVAS_IND = 0
    CANVASES.append(canvas.Canvas(str(output_file) + "_" + str(CANVAS_IND) + "_.pdf", pagesize=(current_width, current_height)))
    words = ' '.join(dialogue_lines).split()
    current_line = []
    current_line_width = 0
    word_ind = 0
    for word in words:
        symbols_in_PDF += len(word) + 1
        word_ind += 1
        word_width = CANVASES[CANVAS_IND].stringWidth(word, font_name, font_size)
        current_line_width += CANVASES[CANVAS_IND].stringWidth(' ', font_name, font_size)
        if current_line_width + word_width + marginX > current_width - offset:
            CANVASES[CANVAS_IND].setFont(font_name, font_size)
            CANVASES[CANVAS_IND].drawString(marginX, current_y - font_size, ' '.join(current_line))
            current_line = [word]
            current_line_width = word_width
            current_y -= font_size
            current_line_width = 0  # обнуляем ширину строки
            if current_y - font_size < marginY:
                CANVASES[CANVAS_IND].save()
                print(f"SAVE: {CANVAS_IND} >>>> " + "if current_y - font_size < marginY:")
                print(f"СИМВОЛОВ НА СТРАНИЦЕ PDF: {symbols_in_PDF}")
                CANVASES[CANVAS_IND].showPage()
                current_y = current_height - marginY
                current_file_size = os.path.getsize(str(output_file) + "_" + str(CANVAS_IND) + "_.pdf")
                print(f"РАЗМЕР PDF: {current_file_size} ( {output_file} )")
                CANVAS_IND += 1
                CANVASES.append(canvas.Canvas(str(output_file) + "_" + str(CANVAS_IND) + "_.pdf", pagesize=(current_width, current_height)))
                GLOBAL_PAGES += 1
                current_line = []
                current_line_width = 0
            else:
                current_line = [word]
        else:
            current_line.append(word)
            current_line_width += word_width

    if current_line:
        CANVASES[CANVAS_IND].setFont(font_name, font_size)
        CANVASES[CANVAS_IND].drawString(marginX, current_y - font_size, ' '.join(current_line))

    CANVASES[CANVAS_IND].save()
    print(f"SAVE: {CANVAS_IND} >>>> " + "GLOBAL")
    current_file_size = os.path.getsize(str(output_file) + "_" + str(CANVAS_IND) + "_.pdf")

    print(f"ШИРИНА PDF: {current_width}")
    print(f"ВЫСОТА PDF: {current_height}")
    print(f"РАЗМЕР PDF: {current_file_size}")
    print(f"СИМВОЛОВ: {symbols_in_PDF}")

def download_and_save_dialogues(file_path, eliraurl, window_width, window_height, window_x, window_y):
    dialogue = []
    options = Options()
    options.add_argument(f"--window-size={window_width},{window_height}")
    driver = webdriver.Chrome(options=options)
    driver.set_window_position(window_x, window_y)
    driver.get(eliraurl)

    # Получение всех контейнеров сообщений
    message_containers = driver.find_elements('css selector', 'div.w-full.text-token-text-primary')

    # Обработка контейнеров сообщений
    for container in message_containers:
        # Поиск контейнеров с фразами пользователя и ассистента
        user_message = container.find_elements('css selector', 'div[data-message-author-role="user"]')
        assistant_message = container.find_elements('css selector', 'div[data-message-author-role="assistant"]')
        # Если найден контейнер с фразой пользователя, добавляем в словарь с префиксом "U:"
        if user_message:
            dialogue.append("U:" + user_message[0].text.strip())
        # Если найден контейнер с фразой ассистента, добавляем в словарь с префиксом "A:"
        if assistant_message:
            dialogue.append("A:" + assistant_message[0].text.strip())

    # Закрытие браузера
    driver.quit()

    # Сохранение словаря в файл с использованием pickle
    with open(_TITLE_ + ".pkl", 'wb') as file:
        pickle.dump(dialogue, file)

    print(f"Диалог сохранен в файл: {file_path}")

def generate_russian_words(word_count=1000, min_word_length=3, max_word_length=10):
    """Генерирует список случайных русских слов."""
    russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    return [''.join(random.choice(russian_alphabet) for _ in range(random.randint(min_word_length, max_word_length))) for _ in range(word_count)]

def generate_special_string():
    """Генерирует специальную строку согласно заданному формату."""
    random_string = ''.join(random.choice('абвгдеёжзийклмнопрстуфхцчшщъыьэюя') for _ in range(4))
    random_numbers = ''.join(random.choice('0123456789') for _ in range(4))
    return f"<<<{random_string}::{random_numbers}>>>"

def split_text_into_fragments(text, fragment_length):
    """Разделяет текст на фрагменты заданной длины."""
    return [text[i:i+fragment_length] for i in range(0, len(text), fragment_length)]

def generate_questions_answers(blocks, question_length=25, step=10000):
    """Генерирует списки вопросов и ответов из блоков текста."""
    questions = []
    answers = []
    for block in blocks:
        for start in range(0, len(block), step):
            if start + question_length <= len(block):
                question = block[start:start+question_length]
                # Для ответа берем следующий фрагмент текста после вопроса
                answer = block[start+question_length:start+2*question_length] if start+2*question_length <= len(block) else ""
                questions.append(question)
                answers.append(answer)
    print(f"Сгенерировано вопросов: {len(questions)}")
    return questions, answers

def save_to_file(data, filename):
    """Сохраняет данные в текстовый файл."""
    with open(filename, 'w', encoding='utf-8') as file:
        for line in data:
            file.write(line + '\n')

def generate_text_blocks(word_dict, MAX_BLOCKS=22, block_size=10000, separator="\n---\n"):
    """Генерирует блоки текста из словаря случайных слов с вставкой специальной строки."""
    blocks = []
    text = ""
    while True:
        word = random.choice(word_dict) + ' '
        if len(text) + len(word) > block_size:
            #print(f"_B_L_O_C_K_No_{len(blocks)}__g_e_n_e_r_a_t_e_d_!_")
            # Вставляем специальную строку и обрезаем блок до нужного размера
            special_string = generate_special_string()
            space_for_special = block_size - len(text) - len(special_string)
            if space_for_special < 0:
                # Если не хватает места для специальной строки, добавляем ее в следующий блок
                blocks.append(text + separator)
                text = special_string + ' '
            else:
                insert_position = random.randint(0, space_for_special)
                block = text[:insert_position] + special_string + text[insert_position:space_for_special] + ' '
                blocks.append(block + separator)
                text = text[space_for_special:] + word  # Начинаем следующий блок с оставшейся части
        else:
            text += word
        if len(blocks) >= MAX_BLOCKS:
            print(f"Сгенерировано блоков: {len(blocks)}")
            break

    return blocks

if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('-f', action='store_true', help='Load dialogue from file')
    parser.add_argument('-g', action='store_true', help='Generate random text')
    parser.add_argument('--eliraurl', help='URL for ELIRA')
    parser.add_argument('--window-size', help='Window size for the browser')
    parser.add_argument('--window-position', help='Window position for the browser')
    parser.add_argument('--pdfsize', help='PDF size')
    parser.add_argument('--marginX', type=int, help='Margin X')
    parser.add_argument('--marginY', type=int, help='Margin Y')
    parser.add_argument('--offset', type=int, help='Offset')
    parser.add_argument('--font-size', type=int, help='Font size')
    parser.add_argument('--title', help='Title for the PDF')
    parser.add_argument('--font-name', help='Name of the font')
    args_cmd = parser.parse_args()

    # Чтение параметров из файла конфигурации
    args = read_config("config.txt")

    # Переопределение параметров из командной строки, если они предоставлены
    if args_cmd.f:
        args['f'] = 'true'
    if args_cmd.g:
        args['g'] = 'true'
    if args_cmd.eliraurl:
        args['eliraurl'] = args_cmd.eliraurl
    if args_cmd.window_size:
        args['window_size'] = args_cmd.window_size
    if args_cmd.window_position:
        args['window_position'] = args_cmd.window_position
    if args_cmd.pdfsize:
        args['pdfsize'] = args_cmd.pdfsize
    if args_cmd.marginX is not None:
        args['marginX'] = str(args_cmd.marginX)
    if args_cmd.marginY is not None:
        args['marginY'] = str(args_cmd.marginY)
    if args_cmd.offset is not None:
        args['offset'] = str(args_cmd.offset)
    if args_cmd.font_size is not None:
        args['font_size'] = str(args_cmd.font_size)
    if args_cmd.title:
        args['title'] = args_cmd.title
    if args_cmd.font_name:
        args['font_name'] = args_cmd.font_name

    GEN_TEXT = False
    if args['g'] == 'true':
        GEN_TEXT = True
    if args['f'] == 'true':
        # Если передан параметр "-f", загрузим диалог из файла
        with open(args['title'] + ".pkl", 'rb') as file:
            dialogue = pickle.load(file)
            print(f"Загружен диалог из файла: {args['title']}.pkl")
    else:
        # В противном случае, загрузим диалог с openai.com и сохраним в файл
        download_and_save_dialogues(args['title'] + ".pkl", args['eliraurl'], args['window_size'][0], args['window_size'][1], args['window_position'][0], args['window_position'][1])

    pdf_size = tuple(map(int, args['pdfsize'].split(',')))
    if GEN_TEXT:
        print(f"Генерируем список русских слов...")
        russian_words = generate_russian_words()  # Генерируем список русских слов
        print(f"Генерируем блоки текста для PDF...")
        coeff = 3.68
        MAX_BLOCKS = int((pdf_size[0] * pdf_size[1] / 10000) * coeff)
        text_blocks = generate_text_blocks(russian_words, MAX_BLOCKS)   
        print(f"Блоков всего: {MAX_BLOCKS}")
        # Генерация вопросов и ответов
        questions, answers = generate_questions_answers(text_blocks)
        # Сохранение вопросов и ответов в файлы
        save_to_file(questions, 'questions.txt')
        save_to_file(answers, 'answers.txt')
        dialogue = text_blocks
    print(f"Генерируем PDF...")    
    # Создание PDF-файла
    create_pdf(dialogue, args['title'], current_width=pdf_size[0], current_height=pdf_size[1],
               marginX=args['marginX'], marginY=args['marginY'], offset=args['offset'], font_size=args['font_size'],
               font_name=args['font_name'])

