from ctypes import *
import time


class FlipMountController:
    """
    ThorLab製電動フリップマウントMFF101の制御用クラス．
    Kinesisがダウンロードされている必要がある．
    シリアルナンバーでデバイスを特定する．
    主に外部から呼ぶのはmove, close．
    """
    def __init__(self, sn: str):
        """

        Args:
            sn: シリアルナンバー(文字列)
        """
        self.interval = 3  # [sec]
        self.pre_order_time = time.time()
        self.state = 0

        if len(sn) != 8:
            raise ValueError(f'Invalid serial number :{sn}')
        if sn[:2] != '37':
            raise ValueError(f'This serial number {sn} seems not to be the one of flip mount.')
        self.sn = c_char_p(sn.encode())

        self.lib = cdll.LoadLibrary(r'C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.FilterFlipper.dll')
        self.lib.TLI_BuildDeviceList()
        self.lib.FF_Open(self.sn)
        self.lib.FF_StartPolling(self.sn, c_int(200))
        self.wait()
        self.lib.FF_ClearMessageQueue(self.sn)

        print(f'Flip mount {self.sn.value.decode()} successfully initialized.')

    def wait(self):
        """
        前に送った命令からの時間がself.intervalより短ければその差分だけtime.sleep()する．
        Returns:

        """
        now = time.time()
        time_to_wait = self.interval - (now - self.pre_order_time)

        if time_to_wait > 0:
            time.sleep(time_to_wait)

        self.pre_order_time = now

    def home(self):
        """
        home (position 1)に移動．
        Returns: bool

        """
        if self.state == 1:
            print(f'The flip mount position is already home.')
            return True
        self.lib.FF_Home(self.sn)
        self.wait()
        self.state = 1

        print(f'Flip mount {self.sn.value.decode()} moved to home.')

        return True

    def move(self, position: int):
        """
        positionを1か2に指定して移動する．
        Args:
            position: integer value for position.

        Returns: bool

        """
        if position not in [1, 2]:
            raise ValueError(f'Invalid position: {position}')
        if position == self.state:
            print(f'The flip mount position is already {position}.')
            return True
        self.lib.FF_MoveToPosition(self.sn, position)
        self.wait()
        self.state = position

        print(f'Flip mount {self.sn.value.decode()} moved to {position}.')

        return True

    def close(self):
        """
        closeする．
        Returns:

        """
        self.lib.FF_ClearMessageQueue(self.sn)
        self.lib.FF_StopPolling(self.sn)
        self.lib.FF_Close(self.sn)

        print(f'Flip mount {self.sn.value.decode()} successfully closed.')

        return True


def main():
    fmc = FlipMountController(sn='37858078')
    fmc.home()
    fmc.move(1)
    fmc.move(2)
    fmc.home()
    fmc.close()


if __name__ == '__main__':
    main()
