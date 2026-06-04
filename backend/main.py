from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import random
from collections import Counter
import os
import uvicorn

app = FastAPI(
    title="Meme Gallery API",
    description="Адаптований бекенд для фронтенду сайту з мемами (Ready for Render)",
    version="1.1.5"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- МОДЕЛІ ---
class MemeCreate(BaseModel):
    url: str = Field(..., description="Посилання на картинку з мемом")
    category: str = Field(..., description="Категорія мему (IT, Коти, Навчання тощо)")

class MemeResponse(MemeCreate):
    id: int = Field(..., description="Унікальний ідентифікатор мему")

class StatsResponse(BaseModel):
    total: int = Field(..., description="Загальна кількість мемів")
    top_category: str = Field(..., description="Найпопулярніша категорія")

# --- БАЗА ДАНИХ (У пам'яті) ---
db_memes: List[MemeResponse] = [
    MemeResponse(id=1, url="https://api.memegen.link/images/fine/code_has_100_errors/this_is_fine.png", category="IT"),
    MemeResponse(id=2, url="https://api.memegen.link/images/rollsafe/cant_have_bugs/if_you_never_test_it.png", category="IT"),
    MemeResponse(id=3, url="https://api.memegen.link/images/woman-cat/why_wont_it_compile/meow.png", category="Коти"),
    MemeResponse(id=4, url="https://api.memegen.link/images/db/studying_for_NMT/me/playing_rust.png", category="Навчання"),
    MemeResponse(id=5, url="https://api.memegen.link/images/drake/sleeping/playing_terraria_until_4_am.png", category="Ігри")
]
current_id = 6

# --- ЕНДПОЇНТИ (ПРАВИЛЬНИЙ ПОРЯДОК) ---

@app.get("/")
def read_root():
    return {"message": "API is running"}

# 1. Статистика (Специфічний шлях — НАЙВИЩЕ)
@app.get("/memes/stats", response_model=StatsResponse, summary="Отримати статистику")
def get_stats():
    if not db_memes:
        return StatsResponse(total=0, top_category="Немає")
    
    categories = [m.category for m in db_memes]
    category_counts = Counter(categories)
    top_category = category_counts.most_common(1)[0][0]
    
    return StatsResponse(total=len(db_memes), top_category=top_category)

# 2. Рандомний мем (Специфічний шлях — ВИЩЕ за загальний /memes)
@app.get("/memes/random", response_model=MemeResponse, summary="Отримати випадковий мем")
def get_random_meme():
    if not db_memes:
        raise HTTPException(status_code=404, detail="У базі ще немає жодного мему")
    return random.choice(db_memes)

# 3. Загальний список (Динамічний шлях — НИЖЧЕ за /stats та /random)
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

# 4. Створення мему
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

# 5. Видалення мему (Перероблено на Query-параметр для безпеки HTTP DELETE)
@app.delete("/memes", status_code=204, summary="Видалити мем по URL")
def delete_meme(url: str = Query(..., description="URL мему, який треба видалити")):
    for index, m in enumerate(db_memes):
        if m.url == url:
            del db_memes[index]
            return
    raise HTTPException(status_code=404, detail="Мем з таким URL не знайдено")

# Блок автозапуску для Render
if __name__ == "__main__":
    # Render передає порт у змінну оточення PORT, якщо її немає — беремо стандартний 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
