# Go 程式碼風格範例

本文件提供此專案 Go 程式碼風格的具體範例，包含良好與不良的實踐對比。

## 實體與外鍵

### ✅ 良好 - foreignKey 放在最尾端

```go
type BlogPost struct {
    ID        uint      `gorm:"primaryKey"`
    Title     string    `gorm:"not null"`
    Content   string    `gorm:"type:text"`
    CreatedAt time.Time
    UserID    uint      `gorm:"not null"` // 外鍵放在最尾端
}
```

### ❌ 不良 - foreignKey 放在中間

```go
type BlogPost struct {
    ID        uint      `gorm:"primaryKey"`
    UserID    uint      `gorm:"not null"` // 外鍵不在最尾端
    Title     string    `gorm:"not null"`
    Content   string    `gorm:"type:text"`
    CreatedAt time.Time
}
```

---

## 請求表單與 GORM 驗證

### ✅ 良好 - 使用 GORM binding，欄位使用 PascalCase

```go
type CreateBlogRequest struct {
    Title   string `form:"Title" binding:"required,min=1,max=200"`
    Content string `form:"Content" binding:"required,min=1"`
    UserID  uint   `form:"UserID" binding:"required"`
}
```

### ❌ 不良 - 另外寫驗證函式

```go
type CreateBlogRequest struct {
    Title   string `form:"title"` // 錯誤：應該使用 PascalCase
    Content string `form:"content"`
    UserID  uint   `form:"user_id"`
}

// 不要另外撰寫驗證函式
func ValidateCreateBlogRequest(req CreateBlogRequest) error {
    if req.Title == "" {
        return errors.New("title is required")
    }
    if len(req.Title) > 200 {
        return errors.New("title too long")
    }
    // ... 更多驗證
    return nil
}
```

---

## 測試命名

### ✅ 良好 - 描述性的情境式命名

```go
func Test_Success_When_UserIsAuthenticated(t *testing.T) {
    // 測試實作
}

func Test_Fail_When_TokenIsExpired(t *testing.T) {
    // 測試實作
}

func Test_Success_When_ValidBlogPostIsCreated(t *testing.T) {
    // 測試實作
}

func Test_Fail_When_TitleExceedsMaxLength(t *testing.T) {
    // 測試實作
}
```

### ❌ 不良 - 通用命名

```go
func TestLogin(t *testing.T) {
    // 這是在測試什麼情境？
}

func TestUserAuth(t *testing.T) {
    // 是成功還是失敗的情況？
}

func TestCreateBlog(t *testing.T) {
    // 描述不夠清楚
}
```

---

## 註解

### ✅ 良好 - 複雜邏輯加上原因說明（為什麼）

```go
func ProcessOrder(order Order) error {
    // 使用樂觀鎖來避免庫存超賣問題
    // 因為高併發情況下可能有多個請求同時處理同一商品
    if order.Status == "pending" {
        for _, item := range order.Items {
            if item.Stock > 0 {
                switch item.Type {
                case "physical":
                    if item.RequiresShipping {
                        // 根據重量和距離計算運費
                        // 因為不同物流商有不同的計價模式
                        if item.Weight > 10 {
                            // ...
                        }
                    }
                }
            }
        }
    }
    return nil
}
```

**複雜度分數**：
- 第 1 個 `if` = 1
- `for` = 1
- 巢狀 `if` = 2 (1 × 2)
- 巢狀 `switch` = 2 (1 × 2)
- 巢狀 `case` + 巢狀 `if` = 4 (2 × 2)
- **總計 = 10 分** → 需要註解 ✅

### ❌ 不良 - 簡單邏輯加上不必要的註解（做什麼）

```go
func GetUser(id uint) (*User, error) {
    // 從資料庫查詢使用者
    var user User
    result := db.First(&user, id)
    // 回傳使用者和錯誤
    return &user, result.Error
}
```

**複雜度分數**：
- 沒有條件判斷或迴圈
- **總計 = 0 分** → 不需要註解

### ✅ 良好 - 簡單邏輯不加註解

```go
func GetUser(id uint) (*User, error) {
    var user User
    result := db.First(&user, id)
    return &user, result.Error
}
```

---

## 檔案組織

### ✅ 良好 - 分離測試檔案

```
blog/
├── create.go              # 核心邏輯
├── create_test.go         # 核心邏輯測試
└── create_validator_test.go  # 驗證器測試
```

### ❌ 不良 - 混合測試類型在同一檔案

```
blog/
├── create.go
└── create_test.go         # 驗證器和邏輯測試混在一起
```

---

## 防衛性編程

### ✅ 良好 - 信任框架和資料庫

```go
func CreateBlog(req CreateBlogRequest) error {
    blog := entity.Blog{
        Title:   req.Title,
        Content: req.Content,
        UserID:  req.UserID,
    }
    return db.Create(&blog).Error
}
```

### ❌ 不良 - 過度的防衛性檢查

```go
func CreateBlog(req CreateBlogRequest) error {
    // 不必要的檢查 - GORM binding 已經驗證過這些了
    if req.Title == "" {
        return errors.New("title is required")
    }
    if len(req.Title) > 200 {
        return errors.New("title too long")
    }
    if req.Content == "" {
        return errors.New("content is required")
    }
    if req.UserID == 0 {
        return errors.New("user ID is required")
    }

    blog := entity.Blog{
        Title:   req.Title,
        Content: req.Content,
        UserID:  req.UserID,
    }

    // 不必要的 nil 檢查 - db 是注入的
    if db == nil {
        return errors.New("database is nil")
    }

    return db.Create(&blog).Error
}
```

---

## API 文件範例

- 做成 md 檔案
- 精簡化
- 一個組合一個 md 檔案，例如: 使用者就是 user.md，購物車就是 cart.md 以此類推

###

--- ✅ 良好
```markdown
# 使用者 API

## 使用者登入

### Request

curl -X POST "api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
    "Email": "email",
    "Password": "password"
}'

### Response

#### 200

{
	"Status": 0,
	"Message": "ok",
	"Data": {
		"UserId": "xxxxxx",
		"Name": "ccccccc"
	}
}

#### 400
{
	"Status": 0,
	"Message": "ok",
	"Errors": ["密碼格式錯誤", "信箱格式錯誤"]
}

```

## 總結

- **實體**：外鍵放最後
- **驗證**：使用 GORM binding 標籤，不要另外寫函式
- **請求表單**：欄位名稱使用 PascalCase
- **測試**：描述性的情境式命名，驗證器測試分離
- **註解**：只在複雜邏輯（分數 > 6）加註解，解釋為什麼而非做什麼
- **簡潔性**：避免過度的防衛性編程
