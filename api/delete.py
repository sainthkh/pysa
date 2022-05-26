import os

dbPath = os.path.join(os.getcwd(), 'db.db')

if os.path.exists(dbPath):
  os.remove(dbPath)
else:
  print("The file does not exist")