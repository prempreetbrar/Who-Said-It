# Author: Prempreet Brar
# Who Said It?

# The Game: A quote is given to the user, and the user must identify the author of the quote.
# 	The user has a fixed number of guesses; if they guess incorrectly, then hints are given to
# 	help them. If they run out of guesses, the game is over. After finishing a game, the user can
# 	choose to quit or continue playing. The user can also save their progress at any time.

# Features: 
# 	- Web-scrapes a given URL for quotes, moving automatically from one page to the next, and
#	  stores the author's name, the quote and the link to the author's bio in a CSV file.
#	- Uses regex expressions to ensure that the user enters an appropriate file name when prompted.
#	- Makes HTTP requests to a given URL for web-scraping.
#	- Uses JSON pickling to allow the user to save the game and resume at any point.

# Limitations:
#	- Web-scrape code needs to be updated if website changes.
#	- Web-scrape delay reduces load on website being scraped, but forces user to wait for scraping
#	  to finish.
#	- No error-handling if user enters in name of .csv file that doesn't exist


from requests import get 						# for http requests		
from bs4 import BeautifulSoup						# for webscraping

from sys import exit                                    # in the event of an error
from time import sleep							# to add a delay between the scraping of pages

from csv import DictReader, DictWriter					# to read and write to a csv
from re import compile							# regex for input validation
from random import choice						# for choosing of random quote
from jsonpickle import encode, decode					# for saving or loading a game

URL = "http://quotes.toscrape.com"
REQUEST_DELAY = 1




class QuoteScraper:
    def __init__(self, parsed_html):
        self._parsed_html = parsed_html
        self._page_exists = True
        self._page_number = 1


    def load_quotes_from_csv(self, file_name):
        quote_file = open_file(file_name, "r")
        csv_reader = DictReader(quote_file)		# iterator containing OrderedDicts
        
        next(csv_reader)				# invoke next to "skip" the row containing headers in the CSV
        quotes = list(csv_reader)
        quote_file.close()
        return quotes


    def update_csv(self, file_name):
        quote_file = open_file(file_name, "w")													
        csv_writer = DictWriter(quote_file, fieldnames = ("Name", "Quote", "Link to Bio"))
        csv_writer.writeheader()
        print()																

        while self._page_exists:
            print(f"Scraping {URL}/page/{self._page_number}, please wait...")

            # dict being written must use headers as keys
            for quote in self._parsed_html.select(".quote"):
                author_name, quote_text, link_to_bio = self._get_info(quote)
                csv_writer.writerow({"Name": author_name, "Quote": quote_text, "Link to Bio": URL + link_to_bio})

            # delay increases time between requests, reducing server load
            sleep(REQUEST_DELAY)
            self._move_to_next_page()

        quote_file.close()
        print(f"\nCreated {file_name} in the current directory.")


    def _get_info(self, quote):
        # use html tags to navigate webpage; used over CSS selectors to avoid having to deal with a list
        author_name = quote.find(class_ = "author").get_text()
        quote_text = quote.find(class_ = "text").get_text()
        link_to_bio = quote.find("a")["href"]
        return author_name, quote_text, link_to_bio


    def _move_to_next_page(self):
        next_page = self._parsed_html.find(class_ = "next")
        # if the next class exists, the URL to the next page is in the anchor tag
        if next_page:
            next_page = URL + next_page.find("a")["href"]
            self._parsed_html = http_request(next_page)
            self._page_number += 1
        else:
            self._page_exists = False




MAX_GUESSES = 5

class UserInterface:
    def __init__(self, list_of_quotes):
        self._list_of_quotes = list_of_quotes

        # quote has not been chosen yet
        self._quote = None
        self._quote_author = None
        self._author_fname = None
        self._author_mname = None
        self._author_lname = None

        self._quote_text = None
        self._author_bio_url = None
        self._remaining_guesses = None
        self._reset()


    def _reset(self):
        random_quote = choice(self._list_of_quotes)
        self._set_game_state(random_quote, MAX_GUESSES)


    def _set_game_state(self, quote, remaining_guesses):
        # quote is read as ordered dict from csv using DictReader; use headings to access desired values
        self._quote = quote
        self._quote_author = quote["Name"]

        # save different parts of author's name to use for hints
        # if author doesn't have middle name, then _author_mname = _author_lname, but this won't affect replacing the name in hints
        author_names = self._quote_author.split()
        self._author_fname = author_names[0]
        self._author_mname = author_names[1]
        self._author_lname = author_names[-1]

        self._quote_text = quote["Quote"]
        self._author_bio_url = quote["Link to Bio"]
        # remaining guesses not hardcoded to MAX_GUESSES, in case user wants to load up a game from a saved jsonpickle file
        self._remaining_guesses = remaining_guesses


    def start(self):
        is_game_on = True

        while is_game_on:
            file_name = input("If you would like to load a saved game from a JSON file, enter the name of the file now (n for new game): ")
            
            if file_name == "n":
                print("\n\nHere's a quote:\n")
                print(self._quote_text)

            else:
                file_name = enforce_file_type("json", file_name)
                self._load_saved_game(file_name)
                print("\n\nHere's a quote:\n")

                print(self._quote_text)
                print("\nHere are all of your previous hints:\n")
                self._display_previous_hints()
                
            is_game_on = self._prompt()
            self._reset()


    def _prompt(self):
        while self._remaining_guesses > 0:
            guess = input(f"\nWho said it? Guesses remaining: {self._remaining_guesses}. Enter the author (or s to save and quit): ")
            
            if guess.lower() == "s":
                self._save_and_quit()
                print("Saved Game. Come back and finish your game later!")
                return False

            # doesn't matter if input is upper or lowercase
            elif guess.lower() != self._quote_author.lower():
                self._remaining_guesses -= 1
                print("\n" + self._get_hint(self._remaining_guesses))

            # if guess is correct then there is no point in continuing to prompt the user
            else:
                print("\nYou guessed correctly! Congratulations!")
                break

        decision = None
        while decision not in ("y", "n"):
            decision = input("Would you like to play again (y/n)? ")[0].lower()

        if decision == "y":
            print("Great! Here we go again...\n\n")
            return True

        print("Thanks for playing! Bye!")
        return False


    # pass in remaining_guesses as a parameter rather than using instance attribute, so that the method can be used when
    # displaying previous hints by passing in specific values
    def _get_hint(self, remaining_guesses):
        match remaining_guesses:
            case 4:
                author_parsed = http_request(self._author_bio_url)
                birthday = author_parsed.find(class_ = "author-born-date").get_text()
                birth_location = author_parsed.find(class_ = "author-born-location").get_text()
                # spaces used over \t for formatting purposes
                return f"    Hint 1: The author was born on {birthday} {birth_location}."				

            case 3:
                return f"    Hint 2: The author's first name starts with {self._author_fname[0]}."

            case 2:
                return f"    Hint 3: The author's last name starts with {self._author_lname[0]}."

            case 1:
                # if the user only has one guess remaining, then take the author's entire bio, replace author's name
                # with blanks including instances where the name is all lowercase, and return the bio; 
                # supposed to be a "strong" hint for the user
                author_parsed = http_request(self._author_bio_url)
                author_bio = author_parsed.find(class_ = "author-description").get_text()
                hidden_bio = author_bio.replace(self._quote_author, "___").replace(self._quote_author.lower(), "___")
                hidden_bio = hidden_bio.replace(self._author_fname, "___").replace(self._author_fname.lower(), "___")
                hidden_bio = hidden_bio.replace(self._author_mname, "___").replace(self._author_mname.lower(), "___")
                hidden_bio = hidden_bio.replace(self._author_lname, "___").replace(self._author_lname.lower(), "___")
                return f"    Hint 4 - here's a short biography of the author:\n {hidden_bio}"

            case 0:
                return f"Sorry, you've run out of guesses. The answer was: {self._quote_author}."

            case _:
                return "You don't get a hint yet! Keep trying!"


    def _display_previous_hints(self):
        # start counting down from one below max guesses until you've displayed all previous hints
        for i in range(MAX_GUESSES - 1, self._remaining_guesses - 1, -1):
            print(self._get_hint(i))
        print()


    # use jsonpickle to store quote rather than pickle because json is more readable than binary
    # use with statement to avoid manually having to close file
    def _save_and_quit(self): 
        save_name = input("Enter the name you want to give for your save file (must end in .json): ")
        enforce_file_type("json", save_name)
        save_file = open_file(save_name, "w")

        json_quote = encode(self._quote) + "\n"
        json_guesses = encode(self._remaining_guesses)
        save_file.writelines([json_quote, json_guesses])
        save_file.close()


    def _load_saved_game(self, file_name):
        save_file = open_file(file_name, "r")

        json_state = save_file.readline()
        saved_state = decode(json_state)
        json_guesses = save_file.readline()
        saved_guesses = decode(json_guesses)

        save_file.close()
        self._set_game_state(saved_state, saved_guesses)




def http_request(url):
    html_webpage = get(url, headers = {"Accept": "plain/HTML"})
    html_string = html_webpage.text
    parsed_html = BeautifulSoup(html_string, "html.parser")
    return parsed_html



# use regex to check if file_name is correct format
def check_file_name(file_format, file_name):
    file_regex = compile(rf"\w+\.{file_format}")
    match_file = file_regex.fullmatch(file_name)
    # match_file can be used as a boolean, since it is None (which is falsy) if there is no match
    return match_file




def enforce_file_type(file_format, file_name):
    is_name_proper = check_file_name(file_format, file_name)
    while not is_name_proper:
        file_name = input(f"Again, please enter a file name that ends in a SINGLE .{file_format}: ")
        is_name_proper = check_file_name(file_format, file_name)

    return file_name




def open_file(file_name, mode):
    try:
        file = open(file_name, mode)
    except FileNotFoundError: 
        print(f"File {file_name} not found in the current directory. Ending game.") 
        exit(1)
    except OSError:
        print(f"An OS error occurred when trying to open {file_name}. Ending game.")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred when opening {file_name}: {repr(e)} Ending game.")
        exit(1)
    return file



def main():
    # get HTTP webpage, if user wants a new file then scrape the webpage and create a new file
    parsed_html = http_request(URL)
    quote_scraper = QuoteScraper(parsed_html)
    should_scrape = input("Do you want a CSV file updated with new quotes (y/n)? ")[0].lower()
    print()

    while should_scrape not in ("y", "n"):
        should_scrape = input("Again, enter y or n if you do or do not want a CSV file updated with new quotes (y/n): ")[0].lower()

    if should_scrape == "y":
        file_name = input("Give a name for the new file (must end in .csv): ")
        file_name = enforce_file_type("csv", file_name)
        quote_scraper.update_csv(file_name)

    file_name = input("Enter the name of a CSV file, with headings [Name], [Quote], [Link to Bio]: ")
    file_name = enforce_file_type("csv", file_name)

    # load the quotes from the CSV and start the application
    list_of_quotes = quote_scraper.load_quotes_from_csv(file_name)
    user_interface = UserInterface(list_of_quotes)
    user_interface.start()

main()
