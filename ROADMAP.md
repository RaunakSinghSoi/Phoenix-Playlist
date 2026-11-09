# Development roadmap

Phoenix Playlist is a working local prototype, but playlist management, automated testing, and robustness still need attention. The estimates below are planning ranges, not completed work.

## 1. Automated tests and repeatable setup (5-7 hours)

- Add unit tests for mood grouping, iTunes response handling, and SQL queries.
- Add Flask endpoint tests using mocked API responses and an isolated SQLite database.
- Document a repeatable verification command and add CI for test runs.

## 2. Manage saved playlists (5-6 hours)

- Rename and delete saved playlists.
- Remove or reorder individual tracks without recreating a playlist.
- Preserve track counts and database relationships after edits.

## 3. API and database reliability (4-6 hours)

- Validate request types, moods, and playlist payloads consistently.
- Handle failed or slow iTunes requests without losing an entire batch.
- Make multi-row playlist saves transactional so a partial failure does not leave inconsistent records.
- Add database migration guidance for changes to the local schema.

## 4. Import and export (4-5 hours)

- Export saved playlists to CSV or JSON.
- Import a previously exported playlist with input validation.
- Check duplicates and clearly report unmatched tracks.

## 5. Frontend and accessibility (4-6 hours)

- Improve result feedback and loading/error states.
- Make saved playlist management usable by keyboard.
- Check mobile layout and improve empty states.

Estimated total: 22-30 hours. The focus is application functionality, tests, and maintenance, not training or benchmarking AI models. Features will be implemented and verified in separate changes.
