from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import random
from collections import Counter

app = FastAPI(
    title="Meme Gallery API",
    description="Адаптований бекенд для фронтенду сайту з мемами",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MemeCreate(BaseModel):
    url: str = Field(..., description="Посилання на картинку з мемом")
    category: str = Field(..., description="Категорія мему (IT, Коти, Навчання тощо)")

class MemeResponse(MemeCreate):
    id: int = Field(..., description="Унікальний ідентифікатор мему")

class StatsResponse(BaseModel):
    total: int = Field(..., description="Загальна кількість мемів")
    top_category: str = Field(..., description="Найпопулярніша категорія")


db_memes: List[MemeResponse] = [
    MemeResponse(id=1, url="https://api.memegen.link/images/fine/code_has_100_errors/this_is_fine.png", category="IT"),
    MemeResponse(id=2, url="https://api.memegen.link/images/rollsafe/cant_have_bugs/if_you_never_test_it.png", category="IT"),
    MemeResponse(id=3, url="https://api.memegen.link/images/woman-cat/why_wont_it_compile/meow.png", category="Коти"),
    MemeResponse(id=4, url="https://api.memegen.link/images/db/studying_for_NMT/me/playing_rust.png", category="Навчання"),
    MemeResponse(id=5, url="https://api.memegen.link/images/drake/sleeping/playing_terraria_until_4_am.png", category="Ігри")
]
current_id = 6


@app.get("/memes/stats", response_model=StatsResponse, summary="Отримати статистику")
def get_stats():
    if not db_memes:
        return StatsResponse(total=0, top_category="Немає")
    
    categories = [m.category for m in db_memes]
    category_counts = Counter(categories)
    top_category = category_counts.most_common(1)[0][0]
    
    return StatsResponse(total=len(db_memes), top_category=top_category)


@app.get("/memes", response_model=List[MemeResponse], summary="Отримати меми з фільтрацією та сортуванням")
def get_memes(
    sort: str = Query("newest", description="Сортування: 'newest' або 'oldest'"),
    category: Optional[str] = Query(None, description="Фільтр за категорією (опціонально)")
):
    result = db_memes.copy()
    
    if category:
        result = [m for m in result if m.category.lower() == category.lower()]
        
    if sort == "oldest":
        result.sort(key=lambda m: m.id)
    else:
        result.sort(key=lambda m: m.id, reverse=True) 
        
    return result


@app.get("/memes/random", response_model=MemeResponse, summary="Отримати випадковий мем")
def get_random_meme():
    if not db_memes:
        raise HTTPException(status_code=404, detail="У базі ще немає жодного мему")
    return random.choice(db_memes)


@app.post("/memes", response_model=MemeResponse, status_code=201, summary="Додати новий мем")
def create_meme(meme: MemeCreate):
    global current_id
    
    if not meme.url.strip() or not meme.category.strip():
        raise HTTPException(status_code=400, detail="Поля 'url' та 'category' не можуть бути порожніми")
        
    new_meme = MemeResponse(
        id=current_id,
        url=meme.url,
        category=meme.category
    )
    db_memes.append(new_meme)
    current_id += 1
    return new_meme


class MemeDelete(BaseModel):
    url: str = Field(..., description="Посилання на мем для видалення")


@app.delete("/memes", status_code=204, summary="Видалити мем по URL")
def delete_meme(meme: MemeDelete):
    for index, m in enumerate(db_memes):
        if m.url == meme.url:
            del db_memes[index]
            return
    raise HTTPException(status_code=404, detail=f"Мем з URL {meme.url} не знайдено для видалення")