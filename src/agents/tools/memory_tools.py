"""Memory Tools - Long-term memory storage and retrieval for Albedo"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent.parent.parent / "data" / "database" / "pm_system.db"
    return sqlite3.connect(db_path)


def store_memory(
    content: str,
    memory_type: str = "fact",
    importance: int = 5,
    project_name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Store important information in long-term memory.

    Args:
        content: The information to remember
        memory_type: Type of memory ('preference', 'decision', 'fact', 'context')
        importance: Importance level 1-10 (10 = critical)
        project_name: Associated project (optional)
        tags: List of tags for categorization

    Returns:
        Confirmation message
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get project_id if project_name provided
    project_id = None
    if project_name:
        cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
        result = cursor.fetchone()
        if result:
            project_id = result[0]

    # Convert tags to JSON
    tags_json = json.dumps(tags) if tags else None

    # Store memory
    cursor.execute("""
        INSERT INTO memories (memory_type, content, project_id, importance, tags)
        VALUES (?, ?, ?, ?, ?)
    """, (memory_type, content, project_id, importance, tags_json))

    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()

    emoji_map = {
        'preference': '⭐',
        'decision': '📋',
        'fact': '💡',
        'context': '📝'
    }
    emoji = emoji_map.get(memory_type, '💾')

    response = f"{emoji} Memory stored (ID: {memory_id})\n"
    response += f"Type: {memory_type.capitalize()}\n"
    response += f"Importance: {importance}/10\n"
    if project_name:
        response += f"Project: {project_name}\n"
    response += f"Content: {content}"

    return response


def recall_memories(
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
    project_name: Optional[str] = None,
    min_importance: int = 5,
    limit: int = 5
) -> str:
    """
    Retrieve relevant memories from long-term memory.

    Args:
        query: Search query (searches in content)
        memory_type: Filter by type
        project_name: Filter by project
        min_importance: Minimum importance level
        limit: Maximum number of memories to retrieve

    Returns:
        Formatted list of memories
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query
    sql = """
        SELECT m.id, m.memory_type, m.content, m.importance, m.tags,
               m.created_at, m.access_count, p.name as project_name
        FROM memories m
        LEFT JOIN projects p ON m.project_id = p.id
        WHERE m.importance >= ?
    """
    params = [min_importance]

    if query:
        sql += " AND m.content LIKE ?"
        params.append(f"%{query}%")

    if memory_type:
        sql += " AND m.memory_type = ?"
        params.append(memory_type)

    if project_name:
        sql += " AND p.name = ?"
        params.append(project_name)

    sql += " ORDER BY m.importance DESC, m.last_accessed DESC LIMIT ?"
    params.append(limit)

    cursor.execute(sql, params)
    memories = cursor.fetchall()

    if not memories:
        conn.close()
        return "No memories found matching your criteria."

    # Update access count and last_accessed for retrieved memories
    memory_ids = [m[0] for m in memories]
    cursor.execute(f"""
        UPDATE memories
        SET access_count = access_count + 1,
            last_accessed = CURRENT_TIMESTAMP
        WHERE id IN ({','.join('?' * len(memory_ids))})
    """, memory_ids)
    conn.commit()
    conn.close()

    # Format response
    emoji_map = {
        'preference': '⭐',
        'decision': '📋',
        'fact': '💡',
        'context': '📝'
    }

    response = f"📚 Retrieved {len(memories)} memories:\n\n"

    for mem in memories:
        mem_id, mem_type, content, importance, tags, created, access_count, proj = mem
        emoji = emoji_map.get(mem_type, '💾')

        response += f"{emoji} [{mem_type.upper()}] (Importance: {importance}/10)\n"
        response += f"   {content}\n"

        if proj:
            response += f"   📁 Project: {proj}\n"

        if tags:
            try:
                tag_list = json.loads(tags)
                response += f"   🏷️ Tags: {', '.join(tag_list)}\n"
            except:
                pass

        response += f"   📊 Accessed: {access_count} times\n\n"

    return response.strip()


def forget_memory(memory_id: int) -> str:
    """
    Remove a memory from long-term storage.

    Args:
        memory_id: ID of the memory to forget

    Returns:
        Confirmation message
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get memory before deleting
    cursor.execute("SELECT content FROM memories WHERE id = ?", (memory_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return f"❌ Memory #{memory_id} not found"

    content = result[0]

    # Delete memory
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()

    return f"🗑️ Forgot memory #{memory_id}: {content[:50]}..."


def get_memory_stats() -> str:
    """
    Get statistics about stored memories.

    Returns:
        Memory statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total memories
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]

    # By type
    cursor.execute("""
        SELECT memory_type, COUNT(*)
        FROM memories
        GROUP BY memory_type
        ORDER BY COUNT(*) DESC
    """)
    by_type = cursor.fetchall()

    # Most important
    cursor.execute("""
        SELECT content, importance
        FROM memories
        ORDER BY importance DESC
        LIMIT 3
    """)
    important = cursor.fetchall()

    conn.close()

    response = f"📊 Memory Statistics:\n\n"
    response += f"Total Memories: {total}\n\n"

    if by_type:
        response += "By Type:\n"
        for mem_type, count in by_type:
            response += f"  • {mem_type.capitalize()}: {count}\n"

    if important:
        response += "\nMost Important:\n"
        for content, importance in important:
            response += f"  • ({importance}/10) {content[:60]}...\n"

    return response
