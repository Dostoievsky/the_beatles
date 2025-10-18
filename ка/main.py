from dataclasses import dataclass, field

@dataclass
class Book:
    name: str
    author: str
    isbn: int
    copies_total: field(default=0, repr=False, compare=False)
    copies_available: field(default=0, repr=False, compare=False)

    def __str__(self):
        return f'{self.name} by {self.author}({self.isbn})'


class Reader:
    def __init__(self, name, age, borrowed_books=None):
        self.name = name
        self.age = age
        if not borrowed_books:
            self.borrowed_books = []
        else:
            self.borrowed_books = borrowed_books

    def take_book(self, book):
        if book.copies_available > 0:
            if book in self.borrowed_books:
                print(f'You have already borrowed the book {book.name}')
            else:
                book.copies_available -= 1
                self.borrowed_books.append(book)
                print(f'You have taken the book {book.name}!')
        else:
            print(f'There are no copies of {book.name} available')

    def return_book(self, book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            book.copies_available += 1
            print(f'You have returned the book {book.name}!')
        else:
            print(f'You have not borrowed the book {book.name}')

    def __repr__(self):
        return f'Reader(name={self.name}, age={self.age}, borrowed_books={self.borrowed_books})'



class Library:
    def __init__(self, books=None, readers=None):
        if readers is None:
            readers = []
        if books is None:
            books = []
        self.books = books
        self.readers = readers

    def add_book(self, book):
        self.books.append(book)
        print(f'The book {book.name} has been added to the library!')

    def add_reader(self, reader):
        self.readers.append(reader)
        print(f'The reader {reader.name} has been added to the library!')

    def all_books(self):
        for book in self.books:
            print(book)

    def borrowed_books(self):
        for book in self.books:
            if not book.copies_available == book.copies_total:
                print(f'{book.name} by {book.author} borrowed: {book.copies_total - book.copies_available}, available: {book.copies_available}')





book1 = Book('Harry Potter', 'J.K. Rowling', 1234, 1, 1)
book2 = Book('Lord of the Rings', 'J.R.R. Tolkien', 5678, 5, 5)

reader1 = Reader('John', 25)
reader2 = Reader('Jane', 30)



reader1.take_book(book1)
reader2.take_book(book2)
reader1.take_book(book2)


library = Library(books=[book1, book2], readers=[reader1, reader2])
library.all_books()
library.borrowed_books()