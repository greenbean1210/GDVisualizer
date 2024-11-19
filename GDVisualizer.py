import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.ticker import FuncFormatter
from sympy import symbols, lambdify, diff
from tkinter import Tk, Label, Entry, Button
import platform

if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic') 
elif platform.system() == 'Darwin': 
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic') 

plt.rcParams['axes.unicode_minus'] = False 


# 축 레이블 마이너스 강제 변환
def force_ascii_minus(ax):
    def formatter(x, pos):
        return '{:.2f}'.format(x).replace('\u2212', '-')
    ax.xaxis.set_major_formatter(FuncFormatter(formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(formatter))

# 심볼릭 변수 정의
x = symbols('x')

# 기본 함수 설정
default_function = "1/3*x**4 - 3*x**2 + 6*x + 4"
default_start = 5.0
default_lr = 0.001
default_iterations = 20

# Tkinter GUI로 함수 입력받기
def open_tkinter_gui():
    def submit():
        try:
            func_str = function_entry.get()
            global f_numeric, f_prime_numeric  
            f = eval(func_str, {"x": x, "np": np})
            f_numeric = lambdify(x, f, "numpy")
            f_prime = diff(f, x)
            f_prime_numeric = lambdify(x, f_prime, "numpy")

            root.destroy()
            open_matplotlib_gui()

        except Exception as e:
            print(f"Error: {e}")

    root = Tk()
    root.title("함수 설정")

    Label(root, text="함수 (f(x)):").grid(row=0, column=0, padx=5, pady=5)
    function_entry = Entry(root, width=40)
    function_entry.insert(0, default_function)
    function_entry.grid(row=0, column=1, padx=5, pady=5)

    Button(root, text="확인", command=submit).grid(row=1, column=0, columnspan=2, pady=10)

    root.mainloop()

# Matplotlib 슬라이더 GUI
def open_matplotlib_gui():
    x_vals = np.linspace(-10, 10, 500)
    y_vals = f_numeric(x_vals)

    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.15, bottom=0.45) 

    fig.canvas.manager.set_window_title("경사 하강법 시각화")
    force_ascii_minus(ax)

    line, = ax.plot(x_vals, y_vals, label=f"f(x)")
    path_points, = ax.plot([], [], 'ro', label="최적화 경로")
    path_line, = ax.plot([], [], linestyle='--', color='gray', linewidth=0.5, label="최적화 경로")    
    ax.set_title("경사 하강법 시각화 도구")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.legend()

    slider_height = 0.03
    ax_start = plt.axes([0.15, 0.3, 0.75, slider_height])
    ax_lr = plt.axes([0.15, 0.2, 0.75, slider_height])
    ax_iter = plt.axes([0.15, 0.1, 0.75, slider_height])

    slider_start = Slider(ax_start, "초깃값", -10, 10.0, valinit=default_start)
    slider_lr = Slider(ax_lr, "학습률", 0.001, 0.1, valinit=default_lr)
    slider_iter = Slider(ax_iter, "시행횟수", 1, 100, valinit=default_iterations, valstep=1)

    # 기울기 하강법 구현
    def gradient_descent(start, learning_rate, iterations):
        x_val = start
        path = [x_val]
        for _ in range(iterations):
            gradient = f_prime_numeric(x_val)
            x_val -= learning_rate * gradient
            path.append(x_val)
        return path

    # 슬라이더 업데이트 
    def update(val):
        start = slider_start.val
        learning_rate = slider_lr.val
        iterations = int(slider_iter.val)

        path = gradient_descent(start, learning_rate, iterations)
        path_y = [f_numeric(p) for p in path]

        path_points.set_data(path, path_y)
        path_line.set_data(path, path_y)  
        fig.canvas.draw_idle()

    slider_start.on_changed(update)
    slider_lr.on_changed(update)
    slider_iter.on_changed(update)

    update(None)

    plt.show()

open_tkinter_gui()