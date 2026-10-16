"""
SYS-ENGINEER ARCADE 198X - MVC ARCHITECTURE
MODEL: threat_model.py
Catálogo de Amenazas Cibernéticas y Tokens de Defensa (Ciberseguridad & Redes TCP/IP)
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CyberThreat:
    id: str
    name: str
    color_hex: str
    icon: str
    ai_strategy: str
    real_world_impact: str
    defense_advice: str


@dataclass
class FirewallToken:
    id: str
    name: str
    spawn_rate: str
    icon: str
    effect: str
    tactical_tip: str


class ThreatModel:
    """Modelo de dominio que gestiona el catálogo de ciberamenazas y defensas."""

    @staticmethod
    def get_all_threats() -> List[CyberThreat]:
        return [
            CyberThreat(
                id="ransomware",
                name="Ransomware (Blinky)",
                color_hex="#ff0044",
                icon="🚨",
                ai_strategy="Persecución Directa (Euclidiana al nodo)",
                real_world_impact="Cifra bases de datos y secuestra archivos exigiendo rescate.",
                defense_advice="Mantén backups inmutables desconectados y segmenta la red."
            ),
            CyberThreat(
                id="phishing",
                name="Phishing (Pinky)",
                color_hex="#ff77bb",
                icon="🎣",
                ai_strategy="Emboscada Anticipada (Intercepción a 4 casillas)",
                real_world_impact="Suplanta identidades para robar credenciales bancarias y tokens.",
                defense_advice="Implementa autenticación multifactor (MFA) y capacitación continua."
            ),
            CyberThreat(
                id="spyware",
                name="Spyware (Inky)",
                color_hex="#00e5ff",
                icon="👁️",
                ai_strategy="Flanqueo por Vector (Pinza coordinada con Ransomware)",
                real_world_impact="Monitorea pulsaciones de teclado y extrae información confidencial.",
                defense_advice="Monitorea tráfico saliente anómalo y usa EDR avanzado."
            ),
            CyberThreat(
                id="trojan",
                name="Trojan (Clyde)",
                color_hex="#ff9900",
                icon="🐴",
                ai_strategy="Merodeo Tímido (Se camufla a distancia corta)",
                real_world_impact="Abre puertas traseras ocultas en software aparentemente inofensivo.",
                defense_advice="Verifica firmas digitales y hashes SHA-256 de ejecutables."
            ),
            CyberThreat(
                id="malware",
                name="Malware Polimórfico (Shadow)",
                color_hex="#aa00ff",
                icon="👾",
                ai_strategy="Infección Caótica (Patrón diagonal impredecible)",
                real_world_impact="Muta su código en cada infección para eludir firmas estáticas.",
                defense_advice="Emplea detección basada en heurística y análisis de comportamiento."
            )
        ]

    @staticmethod
    def get_firewall_tokens() -> List[FirewallToken]:
        return [
            FirewallToken(
                id="antivirus",
                name="Antivirus Endpoint (65%)",
                spawn_rate="65%",
                icon="🛡️",
                effect="Aísla y neutraliza a los virus en modo pánico por 10 segundos.",
                tactical_tip="Aprovecha la ventana para contraatacar y absorber amenazas (+200 a +1600 pts)."
            ),
            FirewallToken(
                id="sniper",
                name="Cyber Sniper (20%)",
                spawn_rate="20%",
                icon="🎯",
                effect="Cañón de pulso láser defensivo con alcance de 10x10 casillas.",
                tactical_tip="Presiona [ESPACIO] o [K] para disparar y eliminar virus a distancia."
            ),
            FirewallToken(
                id="vortex",
                name="Vórtice DDoS Sinkhole (10%)",
                spawn_rate="10%",
                icon="🌀",
                effect="Singularidad electromagnética que absorbe virus en un radio de 7x7 casillas.",
                tactical_tip="Atrae virus agrupados a una trampa de mitigación masiva."
            ),
            FirewallToken(
                id="hardreset",
                name="Hard Reset Cósmico (5%)",
                spawn_rate="5%",
                icon="💥",
                effect="Parche de seguridad global que aniquila instantáneamente todas las amenazas del mapa.",
                tactical_tip="Limpia el nivel de golpe y otorga bonificación masiva de bytes."
            )
        ]
