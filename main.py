from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models, schemas

Base.metadata.create_all(bind=engine)   # 모델대로 테이블을 만든다(이미 있는 테이블은 건너뛴다)
app = FastAPI(title="가계부 API")

# ── 계좌 ─────────────────────────────────────
@app.post("/accounts", response_model=schemas.AccountRead, status_code=201)
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db)):
    account = models.Account(name=payload.name, balance=payload.balance)
    db.add(account)        # ① 세션에 "넣을 예정"으로 등록
    db.commit()            # ② DB에 실제로 INSERT 실행
    db.refresh(account)    # ③ DB가 정해 준 id를 다시 읽어 옴
    return account

@app.get("/accounts", response_model=list[schemas.AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return db.execute(select(models.Account).order_by(models.Account.id)).scalars().all()

@app.get("/accounts/{account_id}", response_model=schemas.AccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다")
    return account

# ── 거래 ─────────────────────────────────────
@app.post("/transactions", response_model=schemas.TransactionRead, status_code=201)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # 계좌가 실제로 있는지 먼저 확인한다 → 없으면 알기 쉬운 404를 돌려준다
    if db.get(models.Account, payload.account_id) is None:
        raise HTTPException(status_code=404, detail="해당 계좌가 없습니다")
    tx = models.Transaction(account_id=payload.account_id, category_id=payload.category_id,
                            amount=payload.amount, memo=payload.memo)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

# 계좌 상세: 계좌 하나를 돌려주면 거래 목록까지 따라 나온다
@app.get("/accounts/{account_id}/detail", response_model=schemas.AccountReadWithTx)
def account_detail(account_id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="계좌 없음")
    return account

# ── 집계 ─────────────────────────────────────
@app.get("/stats/by-category")
def by_category(db: Session = Depends(get_db)):
    stmt = (
        select(models.Category.name, func.sum(models.Transaction.amount), func.count())
        .join(models.Category, models.Transaction.category_id == models.Category.id, isouter=True)
        .where(models.Transaction.amount < 0)     # 지출만
        .group_by(models.Category.name)
    )
    return [{"category": n, "total": t, "count": c} for n, t, c in db.execute(stmt).all()]