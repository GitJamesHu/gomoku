#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五子棋 (Gomoku) - 双人对战游戏
使用 tkinter 实现图形界面，支持 15x15 标准棋盘，黑白双方轮流落子。
"""

import tkinter as tk
from tkinter import messagebox

# ============================================================
# 常量定义
# ============================================================
BOARD_SIZE = 15          # 棋盘大小 15x15
CELL_SIZE = 40           # 每个格子的像素大小
MARGIN = 30              # 棋盘边距
PIECE_RADIUS = 17        # 棋子半径
LINE_WIDTH = 1           # 棋盘线宽

# 窗口尺寸
BOARD_PIXEL = (BOARD_SIZE - 1) * CELL_SIZE
WINDOW_WIDTH = BOARD_PIXEL + MARGIN * 2 + 160  # 右侧信息栏
WINDOW_HEIGHT = BOARD_PIXEL + MARGIN * 2

# 棋盘状态常量
EMPTY = 0
BLACK = 1
WHITE = 2

# 颜色定义
BOARD_COLOR = "#DEB887"       # 棋盘木色
LINE_COLOR = "#5D4037"        # 棋盘线深棕色
BLACK_COLOR = "#212121"       # 黑子
WHITE_COLOR = "#FAFAFA"       # 白子
HIGHLIGHT_COLOR = "#FF5252"   # 获胜高亮色
BG_COLOR = "#FFF8E1"          # 背景色
INFO_BG = "#EFEBE9"           # 信息栏背景


class GomokuGame:
    """五子棋游戏主类"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("五子棋 - Gomoku")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # 游戏状态
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK       # 黑棋先行
        self.game_over = False
        self.win_positions = []           # 获胜的五个位置
        self.move_history = []            # 落子历史（用于悔棋）

        # 创建界面
        self._create_widgets()
        self._draw_board()

    # ----------------------------------------------------------
    # 界面构建
    # ----------------------------------------------------------
    def _create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(padx=10, pady=10)

        # 左侧：棋盘画布
        canvas_width = BOARD_PIXEL + MARGIN * 2
        canvas_height = BOARD_PIXEL + MARGIN * 2
        self.canvas = tk.Canvas(
            main_frame,
            width=canvas_width,
            height=canvas_height,
            bg=BOARD_COLOR,
            highlightthickness=1,
            highlightbackground=LINE_COLOR,
            cursor="hand2",
        )
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self._on_click)

        # 右侧：信息面板
        right_frame = tk.Frame(main_frame, bg=INFO_BG, width=150, height=canvas_height)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        # 标题
        tk.Label(
            right_frame,
            text="五子棋",
            font=("Microsoft YaHei", 20, "bold"),
            bg=INFO_BG,
            fg=LINE_COLOR,
        ).pack(pady=(20, 10))

        # 分隔线
        tk.Frame(right_frame, height=2, bg=LINE_COLOR).pack(fill=tk.X, padx=20, pady=5)

        # 当前玩家指示
        self.status_label = tk.Label(
            right_frame,
            text="",
            font=("Microsoft YaHei", 12),
            bg=INFO_BG,
            fg=LINE_COLOR,
        )
        self.status_label.pack(pady=(15, 5))

        # 指示器（棋子预览）
        self.indicator_canvas = tk.Canvas(
            right_frame, width=40, height=40, bg=INFO_BG, highlightthickness=0
        )
        self.indicator_canvas.pack(pady=(0, 15))

        # 步数显示
        self.move_label = tk.Label(
            right_frame,
            text="步数: 0",
            font=("Microsoft YaHei", 11),
            bg=INFO_BG,
            fg="#757575",
        )
        self.move_label.pack(pady=5)

        # 操作按钮
        btn_config = {
            "font": ("Microsoft YaHei", 11),
            "width": 10,
            "height": 1,
            "relief": tk.RAISED,
            "bd": 2,
        }

        self.reset_btn = tk.Button(
            right_frame,
            text="🔄 重新开始",
            command=self.reset_game,
            bg="#4CAF50",
            fg="white",
            activebackground="#388E3C",
            **btn_config,
        )
        self.reset_btn.pack(pady=(30, 8))

        self.undo_btn = tk.Button(
            right_frame,
            text="↩ 悔棋",
            command=self.undo_move,
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            **btn_config,
        )
        self.undo_btn.pack(pady=5)

        self.quit_btn = tk.Button(
            right_frame,
            text="✕ 退出游戏",
            command=self.root.quit,
            bg="#f44336",
            fg="white",
            activebackground="#D32F2F",
            **btn_config,
        )
        self.quit_btn.pack(pady=5)

        # 快捷键提示
        tk.Label(
            right_frame,
            text="快捷键:\nCtrl+Z 悔棋\nCtrl+R 重新开始",
            font=("Microsoft YaHei", 8),
            bg=INFO_BG,
            fg="#9E9E9E",
            justify=tk.LEFT,
        ).pack(side=tk.BOTTOM, pady=15)

        # 绑定快捷键
        self.root.bind("<Control-z>", lambda _: self.undo_move())
        self.root.bind("<Control-r>", lambda _: self.reset_game())

        self._update_status()

    def _draw_board(self):
        """绘制棋盘网格线和星位点"""
        self.canvas.delete("board")

        # 网格线
        for i in range(BOARD_SIZE):
            # 水平线
            x1, y1 = MARGIN, MARGIN + i * CELL_SIZE
            x2, y2 = MARGIN + BOARD_PIXEL, MARGIN + i * CELL_SIZE
            self.canvas.create_line(x1, y1, x2, y2, fill=LINE_COLOR, width=LINE_WIDTH, tags="board")

            # 垂直线
            x1, y1 = MARGIN + i * CELL_SIZE, MARGIN
            x2, y2 = MARGIN + i * CELL_SIZE, MARGIN + BOARD_PIXEL
            self.canvas.create_line(x1, y1, x2, y2, fill=LINE_COLOR, width=LINE_WIDTH, tags="board")

        # 星位点（天元和四角星）
        star_positions = [
            (3, 3), (3, 7), (3, 11),
            (7, 3), (7, 7), (7, 11),
            (11, 3), (11, 7), (11, 11),
        ]
        star_radius = 3
        for row, col in star_positions:
            cx = MARGIN + col * CELL_SIZE
            cy = MARGIN + row * CELL_SIZE
            self.canvas.create_oval(
                cx - star_radius, cy - star_radius,
                cx + star_radius, cy + star_radius,
                fill=LINE_COLOR, outline="", tags="board"
            )

        # 坐标标注
        for i in range(BOARD_SIZE):
            # 列标（字母）
            self.canvas.create_text(
                MARGIN + i * CELL_SIZE, MARGIN - 16,
                text=chr(ord('A') + i),
                font=("Arial", 9),
                fill=LINE_COLOR,
                tags="board",
            )
            # 行标（数字）
            self.canvas.create_text(
                MARGIN - 16, MARGIN + i * CELL_SIZE,
                text=str(i + 1),
                font=("Arial", 9),
                fill=LINE_COLOR,
                tags="board",
            )

    # ----------------------------------------------------------
    # 棋子绘制
    # ----------------------------------------------------------
    def _draw_piece(self, row: int, col: int, player: int):
        """在指定位置绘制棋子"""
        cx = MARGIN + col * CELL_SIZE
        cy = MARGIN + row * CELL_SIZE
        color = BLACK_COLOR if player == BLACK else WHITE_COLOR

        # 棋子阴影（立体感）
        self.canvas.create_oval(
            cx - PIECE_RADIUS + 2, cy - PIECE_RADIUS + 2,
            cx + PIECE_RADIUS + 2, cy + PIECE_RADIUS + 2,
            fill="#BDBDBD", outline="",
            tags="piece",
        )

        # 棋子主体
        self.canvas.create_oval(
            cx - PIECE_RADIUS, cy - PIECE_RADIUS,
            cx + PIECE_RADIUS, cy + PIECE_RADIUS,
            fill=color, outline="#757575", width=1,
            tags="piece",
        )

        # 白子高光
        if player == WHITE:
            self.canvas.create_oval(
                cx - 6, cy - 6,
                cx + 2, cy + 2,
                fill="", outline="#E0E0E0", width=1,
                tags="piece",
            )

        # 最后落子标记
        self.canvas.create_oval(
            cx - 3, cy - 3,
            cx + 3, cy + 3,
            fill=HIGHLIGHT_COLOR if player == BLACK else "#FF8A80",
            outline="",
            tags="last_move",
        )

    def _highlight_winning_pieces(self):
        """高亮获胜的五个棋子"""
        for row, col in self.win_positions:
            cx = MARGIN + col * CELL_SIZE
            cy = MARGIN + row * CELL_SIZE
            # 红色光晕
            self.canvas.create_oval(
                cx - PIECE_RADIUS - 4, cy - PIECE_RADIUS - 4,
                cx + PIECE_RADIUS + 4, cy + PIECE_RADIUS + 4,
                outline=HIGHLIGHT_COLOR, width=3, dash=(4, 2),
                tags="highlight",
            )

    # ----------------------------------------------------------
    # 事件处理
    # ----------------------------------------------------------
    def _on_click(self, event: tk.Event):
        """处理鼠标点击事件"""
        if self.game_over:
            return

        # 计算最近的交叉点
        col = round((event.x - MARGIN) / CELL_SIZE)
        row = round((event.y - MARGIN) / CELL_SIZE)

        # 检查是否在棋盘范围内
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return

        # 检查是否已有棋子
        if self.board[row][col] != EMPTY:
            return

        # 距离容差检查（防止点到格子中间）
        cx = MARGIN + col * CELL_SIZE
        cy = MARGIN + row * CELL_SIZE
        dist = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
        if dist > PIECE_RADIUS + 2:
            return

        self._place_piece(row, col)

    def _place_piece(self, row: int, col: int):
        """落子"""
        # 记录状态
        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))

        # 清除上一手的标记
        self.canvas.delete("last_move")
        self.canvas.delete("highlight")

        # 绘制棋子
        self._draw_piece(row, col, self.current_player)

        # 检查胜负
        if self._check_win(row, col, self.current_player):
            self.game_over = True
            self._highlight_winning_pieces()
            winner_name = "黑棋 ●" if self.current_player == BLACK else "白棋 ○"
            self.status_label.config(text=f"🎉 {winner_name}\n获胜！")
            self._update_indicator()
            # 延迟弹窗，让高亮先渲染
            self.root.after(200, lambda: messagebox.showinfo(
                "游戏结束", f"{winner_name} 获胜！\n共 {len(self.move_history)} 步"
            ))
        elif len(self.move_history) == BOARD_SIZE * BOARD_SIZE:
            # 平局
            self.game_over = True
            self.status_label.config(text="平局！")
            self._update_indicator()
            self.root.after(200, lambda: messagebox.showinfo("游戏结束", "棋盘已满，平局！"))
        else:
            # 切换玩家
            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self._update_status()

        self.move_label.config(text=f"步数: {len(self.move_history)}")

    def undo_move(self):
        """悔棋"""
        if self.game_over:
            return
        if len(self.move_history) < 2:
            return  # 至少保留最近两步（双方各一步）

        # 撤销两步（双方各悔一步）
        for _ in range(2):
            if not self.move_history:
                break
            row, col, _ = self.move_history.pop()
            self.board[row][col] = EMPTY

        # 重绘
        self.canvas.delete("piece")
        self.canvas.delete("last_move")
        self.canvas.delete("highlight")
        for r, c, player in self.move_history:
            self._draw_piece(r, c, player)

        self.current_player = BLACK if self.move_history and self.move_history[-1][2] == WHITE else BLACK
        self._update_status()
        self.move_label.config(text=f"步数: {len(self.move_history)}")

    # ----------------------------------------------------------
    # 胜负判断
    # ----------------------------------------------------------
    def _check_win(self, row: int, col: int, player: int) -> bool:
        """
        检查 (row, col) 位置落子后是否获胜。
        检查四个方向：水平、垂直、两条对角线。
        """
        directions = [
            (0, 1),    # 水平 →
            (1, 0),    # 垂直 ↓
            (1, 1),    # 对角线 ↘
            (1, -1),   # 对角线 ↙
        ]

        for dr, dc in directions:
            count = 1
            positions = [(row, col)]

            # 正方向延伸
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                positions.append((r, c))
                count += 1
                r += dr
                c += dc

            # 反方向延伸
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                positions.append((r, c))
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                self.win_positions = positions
                return True

        return False

    # ----------------------------------------------------------
    # 状态显示
    # ----------------------------------------------------------
    def _update_status(self):
        """更新状态显示"""
        if self.game_over:
            return
        player_name = "黑棋 ●" if self.current_player == BLACK else "白棋 ○"
        self.status_label.config(text=f"当前回合:\n{player_name}")
        self._update_indicator()

    def _update_indicator(self):
        """更新回合指示器中的棋子"""
        self.indicator_canvas.delete("all")
        if self.game_over:
            return
        color = BLACK_COLOR if self.current_player == BLACK else WHITE_COLOR
        self.indicator_canvas.create_oval(
            5, 5, 35, 35,
            fill=color, outline="#757575", width=1,
        )

    # ----------------------------------------------------------
    # 游戏控制
    # ----------------------------------------------------------
    def reset_game(self):
        """重置游戏"""
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.game_over = False
        self.win_positions = []
        self.move_history = []

        # 清除所有棋子绘制
        self.canvas.delete("piece")
        self.canvas.delete("last_move")
        self.canvas.delete("highlight")

        self._update_status()
        self.move_label.config(text="步数: 0")


def main():
    """程序入口"""
    root = tk.Tk()

    # 居中显示窗口
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - WINDOW_WIDTH) // 2
    y = (screen_h - WINDOW_HEIGHT) // 2
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    game = GomokuGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
