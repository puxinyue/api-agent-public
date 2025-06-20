import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel
from typing import Optional, List
import pymysql
from pymysql import MySQLError
from pymysql.cursors import DictCursor
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
from dbutils.pooled_db import PooledDB
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# pip install bcrypt==3.2.0 passlib==1.7.4
# FastAPI应用初始化
app = FastAPI()

# 配置信息
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'xinyu',
    'db': 'e_shop',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

SECRET_KEY = "your-secret-key-123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 数据库连接池
db_pool = PooledDB(
    creator=pymysql,
    maxconnections=5,
    mincached=2,
    **DATABASE_CONFIG
)


# --- 数据模型 ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone: str


class UserLogin(BaseModel):
    username: str
    password: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category_id: int


class AddressCreate(BaseModel):
    recipient_name: str
    phone: str
    province: str
    city: str
    district: str
    detail_address: str
    is_default: bool = False


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    address_id: int


# --- 响应模型 ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str

class ProductResponse(BaseModel):
    product_id: int
    name: str
    description: str
    price: float
    stock: int
    category_id: int
    is_active: bool

class PaginationInfo(BaseModel):
    page: int
    size: int
    total: int

class ProductListResponse(BaseModel):
    data: List[ProductResponse]
    pagination: PaginationInfo

class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int

class CartResponse(BaseModel):
    cart_items: List[CartItemResponse]

class OrderResponse(BaseModel):
    order_id: int
    order_no: str
    total_amount: float


# --- 工具函数 ---
def get_db_connection():
    try:
        return db_pool.connection()
    except MySQLError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return username
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


# # --- 用户认证相关接口 ---
# @app.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse, responses={
#     201: {"description": "注册成功", "model": MessageResponse},
#     409: {"description": "用户名或邮箱已存在", "model": MessageResponse},
#     422: {"description": "参数校验失败", "model": MessageResponse},
# })
# async def register(user: UserCreate):
#     # 直接存明文密码
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             """
#             INSERT INTO users (username, password_hash, email, phone)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (user.username, user.password, user.email, user.phone)
#         )
#         conn.commit()
#         return {"message": "User registered successfully"}
#     except pymysql.err.IntegrityError as e:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Username or email already exists"
#         )
#     finally:
#         cursor.close()
#         conn.close()


# @app.post("/auth/login", response_model=TokenResponse, responses={
#     200: {"description": "登录成功", "model": TokenResponse},
#     401: {"description": "用户名或密码错误", "model": MessageResponse},
#     422: {"description": "参数校验失败", "model": MessageResponse},
# })
# async def login(form_data: UserLogin):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute(
#         "SELECT * FROM users WHERE username = %s",
#         (form_data.username,))
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     print("user-======>", user)
#     # 明文校验
#     if not user or form_data.password != user['password_hash']:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password"
#         )

#     access_token = create_access_token(data={"sub": user['username']})
#     return {"access_token": access_token, "token_type": "bearer"}


# --- 商品相关接口 ---
@app.get("/products", response_model=ProductListResponse, responses={
    200: {"description": "获取商品列表成功", "model": ProductListResponse},
    422: {"description": "参数校验失败", "model": MessageResponse},
})
async def get_products(
        page: int,  # 必填
        size: int,  # 必填
        category_id: Optional[int] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * size
    query = "SELECT * FROM products WHERE is_active = TRUE"
    params = []

    if category_id:
        query += " AND category_id = %s"
        params.append(category_id)

    query += " LIMIT %s OFFSET %s"
    params.extend([size, offset])

    cursor.execute(query, params)
    products = cursor.fetchall()

    # 获取总数
    count_query = "SELECT COUNT(*) AS total FROM products WHERE is_active = TRUE"
    if category_id:
        count_query += " AND category_id = %s"
        cursor.execute(count_query, (category_id,))
    else:
        cursor.execute(count_query)

    total = cursor.fetchone()['total']
    cursor.close()
    conn.close()

    return {
        "data": products,
        "pagination": {
            "page": page,
            "size": size,
            "total": total
        }
    }


# --- 购物车相关接口 ---
@app.get("/cart", dependencies=[Depends(get_current_user)], response_model=CartResponse, responses={
    200: {"description": "获取购物车成功", "model": CartResponse},
    401: {"description": "未授权，Token无效或缺失", "model": MessageResponse},
    404: {"description": "用户不存在", "model": MessageResponse},
})
async def get_cart(username: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取用户ID
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(
        """
        SELECT p.product_id, p.name, p.price, c.quantity 
        FROM carts c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
        """,
        (user['user_id'],))
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"cart_items": cart_items}


@app.post("/cart/add", response_model=MessageResponse, responses={
    200: {"description": "添加到购物车成功", "model": MessageResponse},
    400: {"description": "库存不足", "model": MessageResponse},

    404: {"description": "用户或商品不存在", "model": MessageResponse},
    422: {"description": "参数校验失败", "model": MessageResponse},
})
async def add_to_cart(
        item: CartItemAdd,
        username: str = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 获取用户ID
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user['user_id']

        # 检查商品
        cursor.execute(
            "SELECT stock FROM products WHERE product_id = %s",
            (item.product_id,))
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product['stock'] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        # 更新购物车
        cursor.execute(
            """
            INSERT INTO carts (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """,
            (user_id, item.product_id, item.quantity)
        )
        conn.commit()
        return {"message": "Item added to cart"}
    finally:
        cursor.close()
        conn.close()


# --- 订单相关接口 ---
@app.post("/orders/create", response_model=OrderResponse, responses={
    200: {"description": "订单创建成功", "model": OrderResponse},
    400: {"description": "购物车为空或地址无效/库存不足", "model": MessageResponse},
    404: {"description": "用户不存在", "model": MessageResponse},
    500: {"description": "订单创建失败", "model": MessageResponse},
})
async def create_order(
        order_data: OrderCreate,
        username: str = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        conn.begin()

        # 获取用户信息
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s",
            (username,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user['user_id']

        # 验证地址
        cursor.execute(
            "SELECT * FROM addresses WHERE address_id = %s AND user_id = %s",
            (order_data.address_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Invalid address")

        # 获取购物车商品
        cursor.execute(
            """
            SELECT c.product_id, c.quantity, p.price, p.stock
            FROM carts c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
            """,
            (user_id,))
        cart_items = cursor.fetchall()
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_amount = 0
        order_no = str(uuid.uuid4())

        # 创建订单
        cursor.execute(
            """
            INSERT INTO orders 
            (user_id, address_id, total_amount, order_no)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, order_data.address_id, 0, order_no))
        order_id = cursor.lastrowid

        # 处理订单项
        for item in cart_items:
            if item['stock'] < item['quantity']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {item['product_id']}"
                )

            subtotal = item['price'] * item['quantity']
            total_amount += subtotal

            # 添加订单项
            cursor.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, item['product_id'], item['quantity'], item['price'])
            )

            # 扣减库存
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                (item['quantity'], item['product_id'])
            )

        # 更新订单金额
        cursor.execute(
            "UPDATE orders SET total_amount = %s WHERE order_id = %s",
            (total_amount, order_id))

        # 清空购物车
        cursor.execute(
            "DELETE FROM carts WHERE user_id = %s",
            (user_id,))

        conn.commit()
        return {
            "order_id": order_id,
            "order_no": order_no,
            "total_amount": total_amount
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Order creation failed: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)