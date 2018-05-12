from tkinter import Canvas, Tk, ALL, ROUND


start_pos = None
draw_start = None
canvas = None
rectangles = []

def start_rect(event):
    global start_pos
    start_pos = event.x, event.y

def end_rect(event):
    global start_pos
    end_pos = event.x, event.y

    rectangles.append((*start_pos, *end_pos))
    start_pos = None

    draw_rectangles()

def drag_rect(event):
    canvas.delete(ALL)
    draw_rectangles()
    canvas.create_rectangle(*start_pos, event.x, event.y)

def draw_rectangles():
    for rectangle in rectangles:
        canvas.create_rectangle(*rectangle)

def start_line(event):
    global draw_start
    draw_start = (event.x, event.y)

def extend_line(event):
    global draw_start
    canvas.create_line(*draw_start, event.x, event.y, width = 5, 
                        capstyle = ROUND)
    draw_start = event.x, event.y

def main():
    root = Tk()
    root.title("PyPaint")

    global canvas
    canvas = Canvas(root, width = 600, height = 600)
    canvas.pack()

    canvas.bind("<Button-1>", start_rect)
    canvas.bind("<ButtonRelease-1>", end_rect)
    canvas.bind("<B1-Motion>", drag_rect)
    canvas.bind("<B2-Motion>", extend_line)
    canvas.bind("<Button-2>", start_line)

    root.mainloop()

if __name__ == "__main__":
    main()
