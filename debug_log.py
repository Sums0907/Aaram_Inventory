import re
with open("uvicorn.log", "r") as f:
    lines = f.readlines()
    for i in range(len(lines)-1, -1, -1):
        if "SQLAlchemyError" in lines[i] or "Database Error" in lines[i] or "IntegrityError" in lines[i] or "ProgrammingError" in lines[i]:
            print("FOUND ERROR AT LINE", i)
            start = max(0, i - 15)
            end = min(len(lines), i + 30)
            for j in range(start, end):
                print(lines[j], end="")
            break
