from datetime import datetime
from sqlalchemy import String, BigInteger, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# 계좌 테이블
class Account(Base):
    __tablename__ = "accounts"                     # 실제 테이블 이름
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    # 이 계좌의 거래 목록 (계좌를 지우면 거래도 같이 지운다)
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan")

# 카테고리 테이블 (같은 이름은 두 번 넣을 수 없다)
class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    kind: Mapped[str] = mapped_column(String(10))

# 거래 테이블: 계좌는 반드시 가리키고, 카테고리는 없어도 된다
class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))            # 외래키
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    memo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    account: Mapped["Account"] = relationship(back_populates="transactions")