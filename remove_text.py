with open("logs.txt", 'r') as f:
    while True:
        with open("reduced_logs.txt", 'w') as f2:
            line = f.readline()
            if not line: break
            if line.find("INFO") == -1 and line.find("info") == -1 and line.find("warn") == -1 and line.find("exited") == -1 and line.find("distribuidos-tp1-rabbitmq-1") == -1:
                print(line)
                f2.write(line)