    <!-- Carte interactive avec coordonnées géographiques réalistes -->
    <div class="carte-senegal">
      <svg viewBox="0 0 800 600" class="senegal-map">
        <!-- Carte réaliste des pôles territoriaux du Sénégal -->
        
        <!-- Pôle Dakar -->
        <!-- Régions: Dakar -->
        <polygon 
          points="200,320 250,300 280,310 290,340 270,370 240,380 210,360 195,340"
          :class="getPoleClass('Dakar')"
          @click="selectPole('Dakar')"
          @mouseover="showTooltip($event, 'Dakar')"
          @mouseleave="hideTooltip"
        />
        <text x="245" y="340" class="pole-label">Dakar</text>
        
        <!-- Pôle Thiès -->
        <!-- Régions: Thiès -->
        <polygon 
          points="180,360 240,380 280,370 310,390 295,420 250,430 200,420 170,390"
          :class="getPoleClass('Thiès')"
          @click="selectPole('Thiès')"
          @mouseover="showTooltip($event, 'Thiès')"
          @mouseleave="hideTooltip"
        />
        <text x="245" y="405" class="pole-label">Thiès</text>
        
        <!-- Pôle Centre (Kaolack, Fatick, Kaffrine) -->
        <!-- Régions: Fatick, Kaffrine, Kaolack -->
        <polygon 
          points="280,310 350,300 420,320 450,360 430,420 380,450 320,440 290,390 280,350"
          :class="getPoleClass('Centre (Kaolack, Fatick, Kaffrine)')"
          @click="selectPole('Centre (Kaolack, Fatick, Kaffrine)')"
          @mouseover="showTooltip($event, 'Centre (Kaolack, Fatick, Kaffrine)')"
          @mouseleave="hideTooltip"
        />
        <text x="370" y="375" class="pole-label">Centre</text>
        
        <!-- Pôle Diourbel-Louga -->
        <!-- Régions: Diourbel, Louga -->
        <polygon 
          points="250,250 350,230 420,250 440,290 420,320 350,300 280,280 250,270"
          :class="getPoleClass('Diourbel-Louga')"
          @click="selectPole('Diourbel-Louga')"
          @mouseover="showTooltip($event, 'Diourbel-Louga')"
          @mouseleave="hideTooltip"
        />
        <text x="345" y="275" class="pole-label">Diourbel-Louga</text>
        
        <!-- Pôle Nord (Saint-Louis) -->
        <!-- Régions: Saint-Louis -->
        <polygon 
          points="180,150 280,140 350,160 380,200 360,240 320,260 250,250 200,220 170,180"
          :class="getPoleClass('Nord (Saint-Louis)')"
          @click="selectPole('Nord (Saint-Louis)')"
          @mouseover="showTooltip($event, 'Nord (Saint-Louis)')"
          @mouseleave="hideTooltip"
        />
        <text x="275" y="200" class="pole-label">Nord</text>
        
        <!-- Pôle Nord-Est (Matam) -->
        <!-- Régions: Matam -->
        <polygon 
          points="380,200 480,180 550,200 580,240 570,290 530,320 460,330 420,290 380,250"
          :class="getPoleClass('Nord-Est (Matam)')"
          @click="selectPole('Nord-Est (Matam)')"
          @mouseover="showTooltip($event, 'Nord-Est (Matam)')"
          @mouseleave="hideTooltip"
        />
        <text x="480" y="255" class="pole-label">Nord-Est</text>
        
        <!-- Pôle Sud-Est (Tambacounda, Kédougou) -->
        <!-- Régions: Kédougou, Tambacounda -->
        <polygon 
          points="450,360 550,340 620,370 680,420 700,480 680,530 620,560 550,550 480,520 430,470 430,420"
          :class="getPoleClass('Sud-Est (Tambacounda, Kédougou)')"
          @click="selectPole('Sud-Est (Tambacounda, Kédougou)')"
          @mouseover="showTooltip($event, 'Sud-Est (Tambacounda, Kédougou)')"
          @mouseleave="hideTooltip"
        />
        <text x="565" y="455" class="pole-label">Sud-Est</text>
        
        <!-- Pôle Sud (Ziguinchor, Sédhiou, Kolda) -->
        <!-- Régions: Kolda, Sédhiou, Ziguinchor -->
        <polygon 
          points="150,450 250,430 320,440 380,450 430,470 480,520 450,570 380,590 300,580 220,570 150,540 120,490"
          :class="getPoleClass('Sud (Ziguinchor, Sédhiou, Kolda)')"
          @click="selectPole('Sud (Ziguinchor, Sédhiou, Kolda)')"
          @mouseover="showTooltip($event, 'Sud (Ziguinchor, Sédhiou, Kolda)')"
          @mouseleave="hideTooltip"
        />
        <text x="300" y="520" class="pole-label">Sud</text>
        
        <!-- Frontières du Sénégal -->
        <path d="M 120,490 L 150,540 L 220,570 L 300,580 L 380,590 L 450,570 L 480,520 L 550,550 L 620,560 L 680,530 L 700,480 L 680,420 L 620,370 L 580,240 L 550,200 L 480,180 L 380,200 L 350,160 L 280,140 L 180,150 L 170,180 L 200,220 L 180,360 L 170,390 L 150,450 L 120,490 Z" 
              fill="none" 
              stroke="#2c3e50" 
              stroke-width="3" 
              class="country-border"/>
      </svg>
    </div>