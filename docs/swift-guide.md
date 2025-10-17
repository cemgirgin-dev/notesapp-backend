# SwiftUI İstemcisi Rehberi

Bu doküman FastAPI tabanlı Notes App backend’i ile haberleşen SwiftUI istemcisi için örnek model ve servis katmanını içerir.

## 1. Temel Ayarlar
- `BASE_URL` = `http://127.0.0.1:8000` (simülatör için). Fiziksel cihazda aynı ağdaki bilgisayar IP’sini kullanın.
- Tüm korumalı uç noktalar JWT token ister. Giriş işlemi sonrası dönen `access_token` değerini `Authorization: Bearer <token>` başlığı ile gönderin.
- Token’ı Keychain’de saklamak önerilir.

```swift
enum API {
    static let baseURL = URL(string: "http://127.0.0.1:8000")!
}
```

## 2. Modeller
```swift
struct AuthResponse: Decodable {
    let accessToken: String
    let tokenType: String

    private enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}

struct UserDTO: Decodable {
    let id: Int
    let email: String
    let createdAt: Date

    private enum CodingKeys: String, CodingKey {
        case id, email
        case createdAt = "created_at"
    }
}

struct NoteDTO: Identifiable, Decodable {
    let id: Int
    let title: String
    let content: String
    let createdAt: Date
    let updatedAt: Date

    private enum CodingKeys: String, CodingKey {
        case id, title, content
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

struct LoginRequest: Encodable {
    let email: String
    let password: String
}

struct SignupRequest: Encodable {
    let email: String
    let password: String
}

struct CreateNoteRequest: Encodable {
    let title: String
    let content: String
}

struct UpdateNoteRequest: Encodable {
    let title: String?
    let content: String?
}
```

> Tarih alanları için backend ISO-8601 formatı döner (`2024-03-05T19:43:01.123456`). `JSONDecoder` `dateDecodingStrategy = .iso8601` olarak ayarlanmalıdır.

## 3. API İstemcisi
```swift
final class APIClient {
    private let session: URLSession
    private var tokenProvider: () -> String?

    init(session: URLSession = .shared, tokenProvider: @escaping () -> String?) {
        self.session = session
        self.tokenProvider = tokenProvider
    }

    func perform<Request: Encodable, Response: Decodable>(
        path: String,
        method: String = "GET",
        body: Request? = nil
    ) async throws -> Response {
        var request = URLRequest(url: API.baseURL.appendingPathComponent(path))
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = tokenProvider() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse, (200..<300).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(Response.self, from: data)
    }
}
```

## 4. Servis Katmanı Örnekleri
```swift
final class AuthService {
    private let client: APIClient

    init(client: APIClient) {
        self.client = client
    }

    func signup(email: String, password: String) async throws -> UserDTO {
        let payload = SignupRequest(email: email, password: password)
        return try await client.perform(path: "auth/signup", method: "POST", body: payload)
    }

    func login(email: String, password: String) async throws -> AuthResponse {
        let payload = LoginRequest(email: email, password: password)
        return try await client.perform(path: "auth/login", method: "POST", body: payload)
    }

    func me() async throws -> UserDTO {
        return try await client.perform(path: "auth/me")
    }
}

final class NotesService {
    private let client: APIClient

    init(client: APIClient) {
        self.client = client
    }

    func list() async throws -> [NoteDTO] {
        try await client.perform(path: "notes/")
    }

    func create(note: CreateNoteRequest) async throws -> NoteDTO {
        try await client.perform(path: "notes/", method: "POST", body: note)
    }

    func update(id: Int, note: UpdateNoteRequest) async throws -> NoteDTO {
        try await client.perform(path: "notes/\(id)", method: "PUT", body: note)
    }

    func delete(id: Int) async throws {
        let _: EmptyResponse = try await client.perform(path: "notes/\(id)", method: "DELETE", body: Optional<EmptyRequest>.none)
    }
}

struct EmptyRequest: Encodable {}
struct EmptyResponse: Decodable {}
```

> `DELETE` uç noktası 204 döndürdüğü için `EmptyResponse` decode edilirken boş içerik hatası almamak adına isteğe özel işleyiş (ör: `perform` fonksiyonunu overload etmek) gerekebilir.

## 5. PDF İndirme
```swift
func downloadPDF(noteID: Int, token: String) async throws -> Data {
    var request = URLRequest(url: API.baseURL.appendingPathComponent("notes/\(noteID)/pdf"))
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    let (data, response) = try await URLSession.shared.data(for: request)
    guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
        throw URLError(.badServerResponse)
    }
    return data // Data'yı `PDFView` veya paylaşım sayfasında kullanabilirsiniz.
}
```

## 6. SwiftUI Örnek Akışı
1. Kayıt veya giriş sonrası `AuthResponse.accessToken` değerini Keychain’de saklayın.
2. `APIClient` içindeki `tokenProvider` token’ı Keychain’den okuyacak şekilde ayarlayın.
3. Not listesini `NotesService.list()` ile çekin ve `@StateObject` view model içinde yayınlayın.
4. Yeni not ekledikten sonra listeyi yenileyin veya optimistik olarak ekleyin.
5. Çıkış yaparken token’ı silin.

Bu yapı üzerine Combine veya AsyncSequence ile daha gelişmiş hata/süreç yönetimi ekleyebilirsiniz.
