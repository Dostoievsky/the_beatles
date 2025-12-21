from something_classes_and_funcs import Database

db = Database()

db.connect()
work_id = db.save_work('test', '12.12.2025', 'test', 'test', 'test', 'test')
db.add_students_from_list('test', ['Test test', 'Test2 test2', 'Test3 test3', 'Test4 test4'])
db.add_submissions_from_answers('test', work_id, {'Test test': 'testttt', 'Test2 test2': 'testtt', 'Test3 testtt3': 'teffst', 'Test4 test4': 'tesfffft'})
db.close()