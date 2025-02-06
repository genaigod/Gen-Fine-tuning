import os
import time
import uuid
from typing import Optional

class FileQueue:
    def __init__(self, queue_dir: str):
        """
        """
        self.queue_dir = queue_dir
        if not os.path.exists(self.queue_dir):
            os.makedirs(self.queue_dir)

    def enqueue(self, data: str):
        """
        """
        file_name = str(uuid.uuid4()) + ".task"
        file_path = os.path.join(self.queue_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)

    def dequeue(self) -> Optional[str]:
        """
        """
        files = sorted(os.listdir(self.queue_dir))
        if not files:
            return None

        file_name = files[0]
        file_path = os.path.join(self.queue_dir, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()

        os.remove(file_path)
        return data

    def size(self) -> int:
        """
        """
        return len(os.listdir(self.queue_dir))

    def clear(self):
        """
        """
        for file_name in os.listdir(self.queue_dir):
            file_path = os.path.join(self.queue_dir, file_name)
            os.remove(file_path)

if __name__ == "__main__":
    queue = FileQueue("my_queue")

    queue.enqueue("Task 1")
    queue.enqueue("Task 2")
    queue.enqueue("Task 3")

    print("Queue size:", queue.size())

    while queue.size() > 0:
        task = queue.dequeue()
        print("Dequeued task:", task)

    queue.clear()
    print("Queue size after clear:", queue.size())