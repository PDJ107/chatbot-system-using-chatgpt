from messages import SpecificFCM
from datetime import datetime, timedelta
import threading
from fastapi import BackgroundTasks


class Timer:
    def __init__(self, background_tasks: BackgroundTasks, message_client: SpecificFCM = None):
        self.message_client = message_client
        self.background_tasks = background_tasks

    def run(
            self,
            query: str
    ) -> str:

        try:
            query = eval(query)
            message = query['message']
            alarm_str = query['time']
        except:
            return 'Wrong query! query format is {"message": "message string", "time": "%Y-%m-%d %H:%M:%S.%f"}'

        now = datetime.now()
        alarm_datetime = datetime.strptime(alarm_str, '%Y-%m-%d %H:%M:%S.%f')

        # if alarm_datetime < now:
        #     alarm_datetime += timedelta(days=1)

        time_diff = (alarm_datetime - now).total_seconds()
        if self.message_client is not None:
            timer = threading.Timer(time_diff, self.message_client.send_message, args=(message, False, True))
        else:
            timer = threading.Timer(time_diff, print, args=(message,))

        self.background_tasks.add_task(timer.start)

        return "메시지 전송 예약이 완료되었습니다."


if __name__ == '__main__':
    timer = Timer()
    timer.run(
        str(
            {
                "message": "timer1",
                'time': str(datetime.now() + timedelta(seconds=5))
            }
        )
    )
