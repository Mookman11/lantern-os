#!/usr/bin/env python3
"""
Peer-to-Peer Mesh Networking
Direct node-to-node communication without central server
Automatic peer discovery and data sync
"""

import sqlite3
import json
import os
import requests
import threading
import time
from datetime import datetime
import hashlib

DB_PATH = "./data/mesh.db"
NODE_ID = os.environ.get('NODE_ID', 'unknown')
MESH_PORT = int(os.environ.get('MESH_PORT', 5001))

def init_mesh_db():
    """Initialize mesh network database"""
    os.makedirs("./data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Peer nodes in mesh
    c.execute('''
        CREATE TABLE IF NOT EXISTS mesh_peers (
            id INTEGER PRIMARY KEY,
            node_id TEXT UNIQUE,
            ip_address TEXT,
            port INTEGER,
            last_sync TIMESTAMP,
            connection_status TEXT DEFAULT 'unknown',
            sync_hash TEXT
        )
    ''')

    # Shared violations (synced across mesh)
    c.execute('''
        CREATE TABLE IF NOT EXISTS mesh_violations (
            id INTEGER PRIMARY KEY,
            violation_id TEXT UNIQUE,
            system_name TEXT,
            violation_type TEXT,
            severity TEXT,
            affected_count INTEGER,
            harm_amount TEXT,
            first_reported TIMESTAMP,
            last_updated TIMESTAMP,
            sync_count INTEGER DEFAULT 1,
            verified_by_peers INTEGER DEFAULT 1
        )
    ''')

    # Mesh sync log
    c.execute('''
        CREATE TABLE IF NOT EXISTS mesh_sync_log (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            peer_node_id TEXT,
            sync_type TEXT,
            items_synced INTEGER,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_mesh_peer(node_id, ip_address, port):
    """Register a peer node in the mesh"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO mesh_peers (node_id, ip_address, port, last_sync)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (node_id, ip_address, port))
    except sqlite3.IntegrityError:
        c.execute('''
            UPDATE mesh_peers
            SET last_sync = CURRENT_TIMESTAMP, connection_status = 'online'
            WHERE node_id = ?
        ''', (node_id,))

    conn.commit()
    conn.close()

def sync_violations_with_peer(peer_node_id, peer_ip, peer_port):
    """Sync violations with a peer node"""
    try:
        # Get our violations
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM mesh_violations')
        our_violations = c.fetchall()
        conn.close()

        # Send to peer
        response = requests.post(
            f'http://{peer_ip}:{peer_port}/mesh/sync',
            json={
                'node_id': NODE_ID,
                'violations': [dict(row) for row in our_violations]
            },
            timeout=5
        )

        if response.status_code == 200:
            # Receive peer's violations
            peer_data = response.json()

            # Merge and store peer violations
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for violation in peer_data.get('violations', []):
                try:
                    c.execute('''
                        INSERT INTO mesh_violations
                        (violation_id, system_name, violation_type, severity,
                         affected_count, harm_amount, first_reported, last_updated, verified_by_peers)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (
                        violation.get('violation_id'),
                        violation.get('system_name'),
                        violation.get('violation_type'),
                        violation.get('severity'),
                        violation.get('affected_count'),
                        violation.get('harm_amount'),
                        violation.get('first_reported'),
                        violation.get('last_updated')
                    ))
                except sqlite3.IntegrityError:
                    c.execute('''
                        UPDATE mesh_violations
                        SET verified_by_peers = verified_by_peers + 1,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE violation_id = ?
                    ''', (violation.get('violation_id'),))

            c.execute('''
                INSERT INTO mesh_sync_log (peer_node_id, sync_type, items_synced, status)
                VALUES (?, ?, ?, ?)
            ''', (peer_node_id, 'violation_sync', len(our_violations), 'success'))

            conn.commit()
            conn.close()

            return True
    except Exception as e:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO mesh_sync_log (peer_node_id, sync_type, items_synced, status)
            VALUES (?, ?, ?, ?)
        ''', (peer_node_id, 'violation_sync', 0, f'failed: {str(e)}'))
        conn.commit()
        conn.close()

    return False

def get_mesh_peers():
    """Get list of all peers in the mesh"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT node_id, ip_address, port FROM mesh_peers')
    peers = [{'node_id': row[0], 'ip': row[1], 'port': row[2]} for row in c.fetchall()]

    conn.close()
    return peers

def get_mesh_violations():
    """Get all violations synced from the mesh"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT violation_id, system_name, violation_type, severity,
               affected_count, harm_amount, verified_by_peers
        FROM mesh_violations
        ORDER BY verified_by_peers DESC, last_updated DESC
    ''')

    violations = [
        {
            'id': row[0],
            'system': row[1],
            'type': row[2],
            'severity': row[3],
            'affected': row[4],
            'harm': row[5],
            'verified_by': row[6]
        }
        for row in c.fetchall()
    ]

    conn.close()
    return violations

def sync_with_mesh():
    """Continuously sync with all peers in the mesh"""
    while True:
        peers = get_mesh_peers()
        for peer in peers:
            sync_violations_with_peer(peer['node_id'], peer['ip'], peer['port'])
        time.sleep(120)  # Sync every 2 minutes

if __name__ == "__main__":
    init_mesh_db()
    print("[OK] Mesh network initialized")
