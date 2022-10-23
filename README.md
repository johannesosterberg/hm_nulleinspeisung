# HM_Nulleinspeisung

Ein kleines Proof of Concept Python Skript, um mittels eines ESP32 mit OpenDTU und einem EHZ Volkszähler Hichi Smartmeter auf Tasmota Basis eine Nulleinspeisung zu realisieren. 

Benötigt werd zusätzlich noch ein laufender MQTT-Broker.

Ich habe, um das Skript zu vereinfachen, das MQTT Topic von OpenDTU von "solar" auf "tele" gestellt, das ist das gleiche Topic wie bei allen Tasmotas.

Vielleicht ist das ja eine Inspiration für den einen oder anderen, ich gebe keine Garantie, dass das Skript funktioniert.
