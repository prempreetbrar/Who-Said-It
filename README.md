# Who-Said-It
A guessing game that scrapes quotes from a website and displays a random quote to the user; the user must guess the quote.

&nbsp;
&nbsp;
&nbsp;




### If you are on MacOS/Linux

1. Ensure you have **Python 3.10.1** or above installed by writing ```python3 --version``` in the terminal; if not, [install Python](https://www.python.org/downloads/), open the .pkg file and follow the steps.
2. Check if you have pip installed by running ```python3 -m pip --version``` in the terminal.
3. If you don't have pip installed, run ```python3 -m ensurepip --default-pip``` in the terminal, and then repeat step 2.

4. Now, in the terminal, do

```
python3 -m pip install requests
python3 -m pip install bs4
python3 -m pip install jsonpickle
```

5. To run the code in the terminal, ensure you are in the directory containing guessing_game.py, and write

```python3 guessing_game.py```

&nbsp;
&nbsp;





### If you are on Windows

1. Ensure you have **Python 3.10.1** or above installed by writing ```py --version``` in the terminal; if not, [install Python](https://www.python.org/downloads/), open the .exe file and follow the steps (make sure the box that says "*Add Python 3.10.X to PATH*" is checked).
2. Check if you have pip installed by running ```py -m pip --version``` in the terminal.
3. If you don't have pip installed, run ```py -m ensurepip --default-pip``` in the terminal, and then repeat step 2.

4. Now, in the terminal, do 

```
py -m pip install requests
py -m pip install bs4
py -m pip install jsonpickle
```

5. To run the code in the terminal, ensure you are in the directory containing guessing_game.py, and write

```py guessing_game.py```



&nbsp;
&nbsp;
&nbsp;

## Limitations/Design Choices

- The scrapy framework would have shortened my code by making scraping easier; I chose to use requests and BeautifulSoup from bs4 to do this "manually", to understand what is happening behind the scenes.
- No delay is needed since the website is intended for scraping (but I added a delay to follow best practices and reduce server load).
- This application could work simply by scraping every time it is run without using a csv, but instead I force the user to load from a csv since it reduces the load on the webpage; it is up to the users discretion if they want to scrape each time or simply load from an existing file (the intention is that you scrape maybe once a week, and use an existing csv for the other times you run the program).

- The quote chosen is supposed to be "random"; I used jsonpickle in-case the user wants to save, quit, and come back later. I used jsonpickle instead of the built-in pickle module because it is more readable.
- *DO NOT put malicious code in the json "saved_game" file you load into the program. The code is automatically executed when it is unpickled from the json file, so malicious code could destroy the program.*
- The "saved_game.json" file is a hardcoded name, which makes it difficult for the user to have multiple save files. I will fix this in a later version.


- No unittests have been implemented; I hope to implement these when I have time. I consider this project "incomplete" because of this.
- There are a few places where I could implement try-except blocks; specifically, for File I/O. I will implement these blocks in the future.
- I used regular expressions to validate some of the filenames; my use of regex isn't that extensive, and I hope to make more use of it in another project.
- I was going to implement an SQLite3 database that can also be used to store quotes; however, there wasn't any analysis necessary on the data so I decided against it; I hope to use SQLite3 in another project.

