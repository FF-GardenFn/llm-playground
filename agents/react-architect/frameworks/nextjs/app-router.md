# Next.js App Router (React Server Components)

**Next.js 13+ App Router**: New routing system built on React Server Components.

App Router fundamentally changes how Next.js applications are built—server-first by default.

---

## Key Concepts

### Server Components (Default)

**All components are Server Components by default** in App Router.

```jsx
// app/page.js - Server Component (default)
async function HomePage() {
  // Can fetch data directly (runs on server)
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()

  return (
    <div>
      <h1>Welcome</h1>
      <p>{json.message}</p>
    </div>
  )
}

export default HomePage
```

**Benefits**:
- Zero JavaScript sent to client (component code stays on server)
- Direct backend access (database, file system, environment variables)
- Better SEO (fully rendered HTML)
- Smaller bundle size

**Limitations**:
- No hooks (useState, useEffect)
- No browser APIs (window, localStorage)
- No event handlers (onClick, onChange)

---

### Client Components ('use client')

**Opt into Client Components** when needed.

```jsx
// app/components/Counter.jsx - Client Component
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

**Use Client Components when**:
- Need state (useState, useReducer)
- Need effects (useEffect)
- Need event handlers (onClick, onChange)
- Need browser APIs (window, localStorage)
- Using libraries that depend on browser

---

## File-Based Routing

### Routing Convention

```
app/
├── page.js                 → / (home)
├── about/
│   └── page.js             → /about
├── blog/
│   ├── page.js             → /blog
│   └── [slug]/
│       └── page.js         → /blog/:slug
└── dashboard/
    ├── layout.js           → Dashboard layout
    ├── page.js             → /dashboard
    └── settings/
        └── page.js         → /dashboard/settings
```

### Special Files

- **page.js**: Defines route UI
- **layout.js**: Shared UI for route and children
- **loading.js**: Loading UI (Suspense fallback)
- **error.js**: Error UI (Error Boundary)
- **not-found.js**: 404 UI
- **template.js**: Re-rendered layout (for animations)

---

## Layouts

**Layouts wrap pages and persist across navigation**:

```jsx
// app/layout.js - Root layout (required)
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
          </nav>
        </header>
        <main>{children}</main>
        <footer>© 2024</footer>
      </body>
    </html>
  )
}
```

```jsx
// app/dashboard/layout.js - Nested layout
export default function DashboardLayout({ children }) {
  return (
    <div className="dashboard">
      <aside>
        <a href="/dashboard">Overview</a>
        <a href="/dashboard/settings">Settings</a>
      </aside>
      <div className="content">{children}</div>
    </div>
  )
}
```

**Benefits**:
- Layouts don't re-render on navigation
- Can nest layouts (app/layout.js → dashboard/layout.js)
- Shared state persists

---

## Data Fetching

### Server Components (Async/Await)

**Fetch data directly in Server Components**:

```jsx
// app/posts/page.js
async function PostsPage() {
  // Fetch runs on server, cached automatically
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 }  // Revalidate every hour
  })
  const posts = await res.json()

  return (
    <div>
      <h1>Posts</h1>
      <ul>
        {posts.map(post => (
          <li key={post.id}>
            <a href={`/posts/${post.id}`}>{post.title}</a>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default PostsPage
```

**Caching options**:
```jsx
// Force cache (default)
fetch('...', { cache: 'force-cache' })

// Never cache
fetch('...', { cache: 'no-store' })

// Revalidate every N seconds
fetch('...', { next: { revalidate: 60 } })
```

---

### Parallel Data Fetching

**Fetch multiple sources in parallel**:

```jsx
async function DashboardPage() {
  // Fetch in parallel (not sequential)
  const [userData, postsData, analyticsData] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
    fetch('/api/analytics').then(r => r.json())
  ])

  return (
    <div>
      <UserProfile user={userData} />
      <PostsList posts={postsData} />
      <Analytics data={analyticsData} />
    </div>
  )
}
```

---

### Loading States

**Use loading.js for automatic loading UI**:

```jsx
// app/posts/loading.js
export default function Loading() {
  return <div>Loading posts...</div>
}
```

**Or use Suspense manually**:

```jsx
import { Suspense } from 'react'

async function Posts() {
  const posts = await fetch('/api/posts').then(r => r.json())
  return <PostsList posts={posts} />
}

export default function PostsPage() {
  return (
    <div>
      <h1>Posts</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <Posts />
      </Suspense>
    </div>
  )
}
```

---

## Dynamic Routes

### [slug] - Dynamic Segments

```jsx
// app/blog/[slug]/page.js
async function BlogPost({ params }) {
  const { slug } = params

  const post = await fetch(`/api/posts/${slug}`).then(r => r.json())

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.body}</p>
    </article>
  )
}

export default BlogPost
```

### generateStaticParams (SSG)

**Pre-render pages at build time**:

```jsx
// app/blog/[slug]/page.js
export async function generateStaticParams() {
  const posts = await fetch('/api/posts').then(r => r.json())

  return posts.map(post => ({
    slug: post.slug
  }))
}

async function BlogPost({ params }) {
  const { slug } = params
  const post = await fetch(`/api/posts/${slug}`).then(r => r.json())

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.body}</p>
    </article>
  )
}

export default BlogPost
```

**Result**: All blog posts pre-rendered at build time (fast!).

---

## Metadata (SEO)

### Static Metadata

```jsx
// app/page.js
export const metadata = {
  title: 'Home | My App',
  description: 'Welcome to my application'
}

export default function HomePage() {
  return <h1>Welcome</h1>
}
```

### Dynamic Metadata

```jsx
// app/blog/[slug]/page.js
export async function generateMetadata({ params }) {
  const { slug } = params
  const post = await fetch(`/api/posts/${slug}`).then(r => r.json())

  return {
    title: post.title,
    description: post.excerpt
  }
}

async function BlogPost({ params }) {
  const { slug } = params
  const post = await fetch(`/api/posts/${slug}`).then(r => r.json())

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.body}</p>
    </article>
  )
}

export default BlogPost
```

---

## Route Handlers (API Routes)

**Create API endpoints in app/api**:

```jsx
// app/api/posts/route.js
import { NextResponse } from 'next/server'

export async function GET(request) {
  const posts = await db.posts.findMany()
  return NextResponse.json(posts)
}

export async function POST(request) {
  const body = await request.json()
  const post = await db.posts.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

**Dynamic route handlers**:

```jsx
// app/api/posts/[id]/route.js
export async function GET(request, { params }) {
  const { id } = params
  const post = await db.posts.findUnique({ where: { id } })

  if (!post) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  return NextResponse.json(post)
}

export async function DELETE(request, { params }) {
  const { id } = params
  await db.posts.delete({ where: { id } })
  return NextResponse.json({ success: true })
}
```

---

## Client-Server Composition

**Mix Server and Client Components**:

```jsx
// app/page.js - Server Component
import ClientCounter from './ClientCounter'

async function HomePage() {
  const data = await fetch('/api/data').then(r => r.json())

  return (
    <div>
      <h1>Welcome</h1>
      <p>Server data: {data.message}</p>

      {/* Client Component nested in Server Component */}
      <ClientCounter initialCount={data.count} />
    </div>
  )
}

export default HomePage
```

```jsx
// app/ClientCounter.jsx - Client Component
'use client'

import { useState } from 'react'

export default function ClientCounter({ initialCount }) {
  const [count, setCount] = useState(initialCount)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

**Rules**:
- ✅ Server Component can import Client Component
- ✅ Server Component can pass props to Client Component
- ❌ Client Component CANNOT import Server Component directly
- ✅ Client Component can receive Server Component as children prop

---

## Streaming (React Suspense)

**Stream content as it's ready**:

```jsx
// app/dashboard/page.js
import { Suspense } from 'react'

async function Analytics() {
  // Slow data fetch (3 seconds)
  const data = await fetch('/api/analytics', { cache: 'no-store' })
    .then(r => r.json())

  return <AnalyticsChart data={data} />
}

async function RecentPosts() {
  // Fast data fetch (0.5 seconds)
  const posts = await fetch('/api/posts/recent')
    .then(r => r.json())

  return <PostsList posts={posts} />
}

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Recent posts load quickly */}
      <Suspense fallback={<div>Loading posts...</div>}>
        <RecentPosts />
      </Suspense>

      {/* Analytics stream in later */}
      <Suspense fallback={<div>Loading analytics...</div>}>
        <Analytics />
      </Suspense>
    </div>
  )
}
```

**Result**: Recent posts appear immediately, analytics load later (no blocking).

---

## Error Handling

### error.js

**Automatic error boundary**:

```jsx
// app/posts/error.js
'use client'  // Error components must be Client Components

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

---

## Best Practices

### 1. Default to Server Components

```jsx
// ✅ Good: Server Component (default)
async function ProductList() {
  const products = await db.products.findMany()
  return <Products data={products} />
}

// ⚠️ Only use Client when necessary
'use client'
function InteractiveProduct() {
  const [selected, setSelected] = useState(null)
  // ...
}
```

**Why**: Server Components = zero JavaScript to client.

---

### 2. Fetch Data Where Needed

```jsx
// ✅ Good: Fetch in component that needs it
async function UserProfile() {
  const user = await fetch('/api/user').then(r => r.json())
  return <Profile user={user} />
}

async function UserPosts() {
  const posts = await fetch('/api/posts').then(r => r.json())
  return <Posts data={posts} />
}

// ❌ Bad: Fetch everything at top level
async function Page() {
  const [user, posts, analytics] = await Promise.all([...])
  // Pass all data down (even if components don't need it yet)
}
```

**Why**: Fetch data close to where it's used (better code splitting).

---

### 3. Use Suspense Boundaries Strategically

```jsx
// ✅ Good: Separate Suspense boundaries
<div>
  <Suspense fallback={<HeaderSkeleton />}>
    <Header />
  </Suspense>

  <Suspense fallback={<ContentSkeleton />}>
    <Content />
  </Suspense>

  <Suspense fallback={<SidebarSkeleton />}>
    <Sidebar />
  </Suspense>
</div>

// ❌ Bad: One Suspense boundary for everything
<Suspense fallback={<FullPageSkeleton />}>
  <Header />
  <Content />
  <Sidebar />
</Suspense>
```

**Why**: Granular loading states (fast parts show first).

---

## Migration from Pages Router

### Key Differences

| Feature | Pages Router | App Router |
|---------|-------------|-----------|
| Routing | pages/ directory | app/ directory |
| Data fetching | getServerSideProps, getStaticProps | async Server Components |
| Layouts | _app.js, _document.js | layout.js (nested) |
| Loading | Custom | loading.js (Suspense) |
| Error | _error.js | error.js (Error Boundary) |
| API | pages/api/ | app/api/ (Route Handlers) |

### Incremental Adoption

**Can use both routers simultaneously**:
```
app/
├── page.js              → / (App Router)
└── dashboard/
    └── page.js          → /dashboard (App Router)

pages/
├── about.js             → /about (Pages Router)
└── blog/
    └── [slug].js        → /blog/:slug (Pages Router)
```

**Migrate route by route** (not all at once).

---

## Summary

**Next.js App Router key concepts**:
- Server Components by default (zero JS to client)
- 'use client' for interactive components
- File-based routing (page.js, layout.js, loading.js, error.js)
- Async data fetching in Server Components
- Streaming with Suspense (progressive loading)
- Metadata API for SEO

**Default to Server Components, opt into Client Components when needed.**
