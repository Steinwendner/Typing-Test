import random
import time
from tkinter import *


class TypingTest:

    def setup_window(self, window):
        """
        Setup of the window, initialize its components and align them
        in a grid.

        :param window: A tkinter window
        """
        window.withdraw()
        window.title("Typing Test")
        window.config(bg="#222",
                      padx=10,
                      pady=10)

        # Transcript - where the text for the user to type is displayed
        window.transcript = Text(window,
                                 width=50, height=2,
                                 font=("Verdana", 24),
                                 state=DISABLED)
        window.transcript.tag_config("correct", background="#aaff90")
        window.transcript.tag_config("wrong", background="#ff9090")
        window.transcript.tag_config("current", background="#b9b9b9")
        window.transcript.tag_config("typed_wrong", foreground="#b11")
        window.transcript.tag_config("typed_correct", foreground="#060")
        window.transcript.grid(column=0, row=0, columnspan=3)

        # Clock
        window.timer = Label(window, text="1:00",
                             bg="#222", fg="#fff",
                             font=("Verdana", 36))
        window.timer.grid(column=1, row=1,
                          pady=(20, 10))

        # Input Frame
        window.inputFrame = Frame(window, bg="#222")
        window.inputFrame.grid(column=1, row=2)

        # Input
        window.input_str = StringVar()
        window.input = Entry(window.inputFrame,
                             font=("Verdana", 24),
                             textvariable=self.window.input_str)
        window.input.bind("<KeyRelease>", self.keyboard_entry)
        window.input.grid(column=0, row=0)

        # Redo/Start - button which starts a typing test
        window.redo = Button(window.inputFrame, text="Start",
                             bg="#ff4500", fg="#fff",
                             padx=10, pady=10)
        window.redo.config(command=self.start_test)
        window.redo.grid(column=1, row=0, padx=(10, 0))

        # Score
        window.scoreLabel = Label(window, text="Press start to test your typing speed!",
                                  bg="#222", fg="#fff",
                                  font=("Verdana", 18))
        window.scoreLabel.grid(column=1, row=3,
                               pady=(30, 5))

    def __init__(self):
        self.window = Tk()
        self.setup_window(self.window)

        # init
        self.word_limit = 200
        self.words = self.get_words()
        self.transcript_lines = []
        self.curr_index = 0
        self.curr_words = []
        self.score = 0
        self.running = False
        self.started_typing = False
        self.start_time = None
        self.test_duration = 60
        self.ico = PhotoImage(file="res/typing_test.gif")

        self.window.update_idletasks()
        self.window.tk.call('wm', 'iconphoto', self.window._w, self.ico)
        self.center_window()
        self.window.wm_resizable(0, 0)
        self.window.deiconify()
        self.window.mainloop()

    def keyboard_entry(self, event):
        """
        Handles keyboard events in the input field

        :param event: the captured event
        """

        # if no test is running, ignore input
        if not self.running:
            return

        # only start the timer once the user starts typing
        if not self.started_typing:
            self.start_time = time.time()
            self.update_clock()
            self.started_typing = True

        # gets the current text in the input field
        current_text = self.window.input_str.get().strip()

        if event.char == ' ':
            if current_text == self.curr_words[self.curr_index]:  # entry was correct
                for c in current_text:
                    self.score += 2 if c.isupper() else 1
                self.score += 1
                self.set_tag("typed_correct")
            else:  # entry was wrong
                self.set_tag("typed_wrong")

            if self.curr_index == len(self.curr_words) - 1:  # was last word, init next line
                self.transcript_lines.append(self.generate_line())
                self.curr_words = self.transcript_lines[-2].split()
                self.set_transcript_text(self.transcript_lines[-2] + "\n" + self.transcript_lines[-1])
                self.curr_index = 0
                self.window.input_str.set("")
                self.remove_all_tags()
                self.set_tag("current")
            else:
                self.curr_index += 1

            self.window.input_str.set("")
            self.set_tag("current")
        elif len(current_text) == 0:
            self.set_tag("current")
        else:
            ctl = len(current_text)
            if current_text == self.curr_words[self.curr_index][0:ctl]:
                self.set_tag("correct")
            else:
                self.set_tag("wrong")

    def start_test(self):
        """ Starts the test after the redo/start button is pressed """

        # reset the list of lines, two new ones and display them
        self.transcript_lines = [self.generate_line(), self.generate_line()]
        self.set_transcript_text(self.transcript_lines[0] + "\n" + self.transcript_lines[1])

        self.curr_words = self.transcript_lines[0].split()
        self.curr_index = 0

        self.set_tag("current")

        self.window.input_str.set("")
        self.window.input.focus_set()

        self.window.scoreLabel.config(text="Your speed is currently being tested.")

        self.running = True

    def update_clock(self):
        """ Update the clock to display the remaining test time """
        time_passed = time.time() - self.start_time
        time_remaining = self.test_duration - time_passed

        if time_remaining <= 0:
            self.running = False
            self.started_typing = False

            self.window.timer.config(text="00:00")

            self.window.input_str.set("")

            self.score = self.score / 5
            self.score = self.score / (self.test_duration / 60)
            self.window.scoreLabel.config(text="Your speed is: {:3d}wpm".format(int(self.score)))
            self.score = 0

            self.set_transcript_text("Time's up!")
            return

        now = "{:02d}:{:02d}".format(int(time_remaining / 60),
                                     int(time_remaining % 60))
        self.window.timer.config(text=now)
        self.window.after(250, self.update_clock)

    def set_tag(self, tag_name):
        """ Set a tag for the last typed word """
        self.remove_background_tags()
        tag_start = self.get_curr_char_index()
        tag_end = tag_start + len(self.curr_words[self.curr_index])
        self.window.transcript.tag_add(tag_name, "1.{}".format(tag_start), "1.{}".format(tag_end))

    def get_curr_char_index(self):
        """
        Gets the index of the last entered character

        :return: position of the last typed character
        """
        return_val = 0
        for i in range(0, self.curr_index):
            return_val += len(self.curr_words[i])
        return_val += self.curr_index
        return return_val

    def remove_all_tags(self):
        """ Removes all tags from the transcript """
        for t in self.window.transcript.tag_names():
            self.window.transcript.tag_remove(t, 1.0, END)

    def remove_background_tags(self):
        """
        Only removes background tags which display whether or
        not the currently typed word is spelled correctly.
        """
        tags = ["current", "correct", "wrong"]
        for t in tags:
            self.window.transcript.tag_remove(t, 1.0, END)

    @staticmethod
    def get_words():
        """Returns the most spoken words from a language file"""
        data = open("res/english_words_2k.txt").read()

        words = []
        for line in str(data).split("\n"):
            words.append(line.split()[1])
        return words

    def generate_line(self):
        """ Returns a line of words chosen randomly from the words list """
        line = ""

        # append a new word until the line length is exceeded
        while True:
            rand = random.randint(0, self.word_limit - 1)
            next_word = self.words[rand]

            max_line_width = 57

            if len(line) + len(next_word) > max_line_width:
                return line
            elif len(line) + len(next_word) == max_line_width:
                return line + next_word

            line += next_word + " "

    def center_window(self):
        """ Center the window on the screen """
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        left = int(self.window.winfo_screenwidth() / 2 - window_width / 2)
        top = int(self.window.winfo_screenheight() / 3 - window_height / 2)
        self.window.geometry("+{}+{}".format(left, top))

    def set_transcript_text(self, string):
        """ Setter method for the transcript """
        self.window.transcript.config(state=NORMAL)
        self.window.transcript.delete("0.0", END)
        self.window.transcript.insert("0.0", string)
        self.window.transcript.config(state=DISABLED)


if __name__ == "__main__":
    TypingTest()
