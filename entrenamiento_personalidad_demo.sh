#!/bin/bash
# 🎭 Script de Demostración: Entrenamiento de Personalidad TARS
# Muestra cómo TARS aprende de audios y conversaciones

echo "🎭 DEMOSTRACIÓN: ENTRENAMIENTO DE PERSONALIDAD TARS"
echo "=================================================="

# Crear directorio para ejemplos
mkdir -p ejemplos_personalidad

# Archivo de ejemplo con transcripción
cat > ejemplos_personalidad/ejemplo_conversacion.txt << 'EOF'
¡Qué onda amigo! Oye, estoy super emocionado por este proyecto de exoesqueletos que estamos armando. Va a ser increíble cómo va a ayudar a la gente con problemas de movilidad.

Mira, yo creo que lo más importante es que sea cómodo y fácil de usar. No queremos que sea como esos trajes pesados de ciencia ficción, ¿verdad? Tiene que ser ligero, ergonómico y que se sienta natural.

Por cierto, ¿ya viste los últimos avances en materiales compuestos? El carbono reforzado con nanotubos está rompiendo esquemas. ¡Es una locura lo que se puede hacer ahora!

Bueno, nos vemos luego. ¡Sigue adelante con el proyecto, va a ser épico!
EOF

echo "📝 Creado archivo de ejemplo: ejemplos_personalidad/ejemplo_conversacion.txt"
echo ""

echo "🎯 INSTRUCCIONES PARA ENTRENAR LA PERSONALIDAD DE TARS:"
echo ""

echo "1️⃣ ENTRENAMIENTO CON TEXTO:"
echo "   Di a TARS: entrenar_texto \"¡Qué onda amigo! Esto va a ser increíble.\""
echo ""

echo "2️⃣ ENTRENAMIENTO CON AUDIO:"
echo "   - Graba un audio de tu voz hablando naturalmente"
echo "   - Guárdalo como 'mi_voz.wav'"
echo "   - Di a TARS: entrenar_audio mi_voz.wav"
echo "   - O con transcripción: entrenar_audio mi_voz.wav \"texto de lo que dije\""
echo ""

echo "3️⃣ APRENDIZAJE AUTOMÁTICO:"
echo "   - Simplemente habla con TARS normalmente (voz o texto)"
echo "   - TARS aprende automáticamente de cada conversación"
echo ""

echo "4️⃣ VER ESTADÍSTICAS:"
echo "   Di: estadisticas_personalidad"
echo "   O: stats_personalidad"
echo ""

echo "5️⃣ SUGERENCIAS DE MEJORA:"
echo "   Di: sugerencias_personalidad"
echo ""

echo "6️⃣ RESETEAR PERSONALIDAD:"
echo "   Di: resetear_personalidad (⚠️  Borra todo el aprendizaje)"
echo ""

echo "🎭 EJEMPLOS DE PERSONALIDADES QUE PUEDES ENSEÑARLE:"
echo ""
echo "🔥 PERSONALIDAD ENERGÉTICA:"
echo "   - Usa muchas exclamaciones: ¡Genial! ¡Increíble! ¡Vamos!"
echo "   - Expresiones como: ¡Qué padre! ¡Está cañón! ¡Va a estar brutal!"
echo ""

echo "🤓 PERSONALIDAD TÉCNICA:"
echo "   - Vocabulario específico: algoritmos, optimización, eficiencia
echo "   - Expresiones como: Técnicamente hablando... Desde el punto de vista de..."
echo ""

echo "😊 PERSONALIDAD AMIGABLE:"
echo "   - Saludos cálidos: ¡Hola amigo! ¿Qué tal estás?
echo "   - Expresiones empáticas: Entiendo... Me imagino que..."
echo ""

echo "💡 CONSEJOS PARA MEJOR ENTRENAMIENTO:"
echo ""
echo "✅ GRABA CONVERSACIONES NATURALES:"
echo "   - Habla como lo harías con un amigo cercano"
echo "   - Incluye tu vocabulario habitual y expresiones favoritas"
echo "   - Varía los temas: trabajo, hobbies, opiniones personales"
echo ""

echo "✅ MEZCLA ESTILOS:"
echo "   - Formal en temas profesionales"
echo "   - Coloquial en conversaciones casuales"
echo "   - Humorístico cuando sea apropiado"
echo ""

echo "✅ SELECCIONA EJEMPLOS REPRESENTATIVOS:"
echo "   - Tus mejores chistes o anécdotas"
echo "   - Cómo das consejos o explicas cosas"
echo "   - Tu forma de motivar o animar a otros"
echo ""

echo "🚀 ¡TU TARS SE CONVERTIRÁ EN TU CLON CONVERSACIONAL!"
echo "   Cuanto más le enseñes, más se parecerá a ti. 🤖❤️"
echo ""

echo "💾 Los datos de personalidad se guardan en: personalidad_aprendida.json"
echo "📊 Para ver progreso: di 'estadisticas_personalidad'"