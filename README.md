# GridMaster

## Для разработиков
### Первоначальная настройка
1. Активируем виртуальную среду разработки
2. Переходим в директорию, содержащую этот файл, используя команду `cd <path>`
3. Ставим зависимости `pip install -r dev_requirements.txt`
4. Установим pre-commit `pre-commit install` (Опционально)

### Использование и разработка
1. Для запуска `python main.py` или `python3 main.py`
2. Для запуска тестов `pre-commit run -a`

## Для обычного пользователя
1. Активируем виртуальную среду разработки
2. Переходим в директорию, содержащую этот файл, используя команду `cd <path>`
3. Ставим зависимости `pip install -r prod_requirements.txt`
4. Для запуска используем `python main.py` или `python3 main.py`

## Сборка в исполняемый файл
1. Переходим в директорию, расположенную на 1 выше, чем та, что содержит этот файл, используя команду `cd <path>`
2. Создаём новую среду разработки и активируем её `python -m venv .buildvenv`
3. Активируем её
    + Для Windows `.\.buildvenv\Scripts\activate`
    + Для Linux и MacOS `source ./.buildvenv/bin/activate`
4. Устанавливаем зависимости `pip install -r ./grid-interpreter/prod_requirements.txt`
5. Устанавливаем [Pyinstaller](https://pyinstaller.org/en/stable/) `pip install pyinstaller Pillow`
6. Собираем исполняемый файл `pyinstaller ./grid-interpreter/main.py -w -F -n "Grid Master" -i ./grid-interpreter/ui/assets/logo_512.png --add-data ./grid-interpreter/ui:./ui`

### Видеоматериалы, демонстрирующие работу интерпретатора
[Ссылка](https://www.youtube.com/watch?v=Pc_LbVsZmGo&ab_channel=%D0%93%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D0%BB%D0%A1%D1%83%D1%81%D0%BB%D0%B8%D0%BA) на видео
