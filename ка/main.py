class Testpaper:
    def __init__(self, topic, right_answers, percantage):
        self.topic = topic
        self.right_answers = right_answers
        self.percantage = int(percantage[:-1])


class Student:
    def __init__(self):
        self.tests_taken = 'No tests taken'

    def take_test(self, paper_test, student_test):
        if type(self.tests_taken) == str:
            self.tests_taken = {}
        correct = sum(1 for st, rig in zip(student_test, paper_test.right_answers) if st == rig)
        percentage = round((correct / len(paper_test.right_answers)) * 100)

        result = "Passed!" if percentage >= paper_test.percantage else "Failed!"
        self.tests_taken[paper_test.topic] = f"{result} ({percentage}%)"


# TEST_1:
paper1 = Testpaper('Maths', ['1A', '2C', '3D', '4A', '5A'], '60%')
paper2 = Testpaper('Chemistry', ['1C', '2C', '3D', '4A'], '75%')
paper3 = Testpaper('Computing', ['1D', '2C', '3C', '4B', '5D', '6C', '7A'], '75%')

student1 = Student()
student2 = Student()

student1.take_test(paper1, ['1A', '2D', '3D', '4A', '5A'])
student2.take_test(paper2, ['1C', '2D', '3A', '4C'])
student2.take_test(paper3, ['1A', '2C', '3A', '4C', '5D', '6C', '7B'])

print(student1.tests_taken)
print(student2.tests_taken)