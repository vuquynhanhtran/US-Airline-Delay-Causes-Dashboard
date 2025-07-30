'''
Mỗi nút của cây có trường id (số nguyên duy nhất, không trùng lặp)
Thực hiện 1 chuỗi các hành động sau đây bao gồm các thao tác liên quan đến xây dựng cây và duyệt cây:
MakeRoot u: Tạo ra nút gốc u của cây
Insert u v: tạo mới 1 nút u và chèn vào cuối danh sách nút con của nút v
PreOrder: in ra thứ tự các nút trong phép duyệt cây theo thứ tự trước
InOrder: in ra thứ tự các nút trong phép duyệt cây theo thứ tự giữa
PostOrder: in ra thứ tự các nút trong phép duyệt cây theo thứ tự sau
Dữ liệu: bao gồm các dòng, mỗi dòng là 1 trong số các hành động được mô tả ở trên, dòng cuối dùng là * (đánh dấu sự kết thúc của dữ liệu).
Kết quả: ghi ra trên mỗi dòng, thứ tự các nút được thăm trong phép duyệt theo thứ tự trước, giữa, sau của các hành động $PreOrder, $InOrder, $PostOrder tương ứng đọc được từ dữ liệu đầu vào
Ví dụ
Dữ liệu
MakeRoot 10
Insert 11 10
Insert 1 10
Insert 3 10
InOrder
Insert 5 11
Insert 4 11
Insert 8 3
PreOrder
Insert 2 3
Insert 7 3
Insert 6 4
Insert 9 4
InOrder
PostOrder
*
Kết quả
11 10 1 3
10 11 5 4 1 3 8
5 11 6 4 9 10 1 8 3 2 7
5 6 9 4 11 1 8 2 7 3 10
'''

forest = {} 

class Tree:
    def __init__(self, val=0) -> None:
        self.child = []
        self.val = val
    def make_root(self, u: int) -> None:
        self.val = u
        forest[u] = self
    def insert(self, u: int, v: int) -> None:
        par_tree = forest[v]
        baby_tree = Tree(u)
        forest[u] = baby_tree
        par_tree.child.append(baby_tree)
    def pre_order(self, cur) -> None:
        print(cur.val, end=" ")
        for i in cur.child:
            self.pre_order(i)
    def in_order(self, cur) -> None:
        if not cur.child:
            print(cur.val, end=" ")
            return
        out = True
        for i in cur.child:
            self.in_order(i)
            if out:
                print(cur.val, end=" ")
                out = False
    def post_order(self, cur) -> None:
        for i in cur.child:
            self.post_order(i)
        print(cur.val, end=" ")

root = Tree()
while True:
    inp = input().split()
    if inp[0] == "*":
        break
    if inp[0] == "MakeRoot":
        root.make_root(int(inp[1]))
    elif inp[0] == "Insert":
        u, v = map(int, inp[1:])
        root.insert(u, v)
    elif inp[0] == "InOrder":
        root.in_order(root)
        print()
    elif inp[0] == "PreOrder":
        root.pre_order(root)
        print()
    else:
        root.post_order(root)
        print()

