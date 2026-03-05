<template>
  <div class="phone-input-wrapper">
    <input
      ref="input"
      type="tel"
      :value="displayValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      @input="onInput"
      @blur="onBlur"
      class="phone-input"
    />
  </div>
</template>

<script>
export default {
  name: 'PhoneInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '+221 77 123 45 67'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    defaultIndicatif: {
      type: String,
      default: '+221'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      displayValue: ''
    };
  },
  watch: {
    modelValue: {
      immediate: true,
      handler(newVal) {
        this.displayValue = this.formatPhone(newVal || '');
      }
    }
  },
  mounted() {
    // Ne pas pré-remplir l'indicatif automatiquement
  },
  methods: {
    // Patterns de formatage par pays
    getCountryPattern(indicatif) {
      const patterns = {
        // Sénégal: +221 XX XXX XX XX (9 chiffres)
        '+221': { groups: [2, 3, 2, 2], length: 9 },
        // France: +33 X XX XX XX XX (9 chiffres)
        '+33': { groups: [1, 2, 2, 2, 2], length: 9 },
        // Belgique: +32 XXX XX XX XX (9 chiffres)
        '+32': { groups: [3, 2, 2, 2], length: 9 },
        // Suisse: +41 XX XXX XX XX (9 chiffres)
        '+41': { groups: [2, 3, 2, 2], length: 9 },
        // USA/Canada: +1 XXX XXX XXXX (10 chiffres)
        '+1': { groups: [3, 3, 4], length: 10 },
        // Royaume-Uni: +44 XXXX XXX XXX (10 chiffres)
        '+44': { groups: [4, 3, 3], length: 10 },
        // Allemagne: +49 XXX XXXXXXX (variable)
        '+49': { groups: [3, 7], length: 10 },
        // Espagne: +34 XXX XXX XXX (9 chiffres)
        '+34': { groups: [3, 3, 3], length: 9 },
        // Italie: +39 XXX XXX XXXX (10 chiffres)
        '+39': { groups: [3, 3, 4], length: 10 },
        // Maroc: +212 X XX XX XX XX (9 chiffres)
        '+212': { groups: [1, 2, 2, 2, 2], length: 9 },
        // Côte d'Ivoire: +225 XX XX XX XX XX (10 chiffres)
        '+225': { groups: [2, 2, 2, 2, 2], length: 10 },
        // Mali: +223 XX XX XX XX (8 chiffres)
        '+223': { groups: [2, 2, 2, 2], length: 8 },
        // Guinée: +224 XXX XX XX XX (9 chiffres)
        '+224': { groups: [3, 2, 2, 2], length: 9 },
        // Burkina Faso: +226 XX XX XX XX (8 chiffres)
        '+226': { groups: [2, 2, 2, 2], length: 8 },
        // Niger: +227 XX XX XX XX (8 chiffres)
        '+227': { groups: [2, 2, 2, 2], length: 8 },
        // Togo: +228 XX XX XX XX (8 chiffres)
        '+228': { groups: [2, 2, 2, 2], length: 8 },
        // Bénin: +229 XX XX XX XX (8 chiffres)
        '+229': { groups: [2, 2, 2, 2], length: 8 },
        // Mauritanie: +222 XX XX XX XX (8 chiffres)
        '+222': { groups: [2, 2, 2, 2], length: 8 },
        // Gambie: +220 XXX XXXX (7 chiffres)
        '+220': { groups: [3, 4], length: 7 },
        // Guinée-Bissau: +245 XXX XXXX (7 chiffres)
        '+245': { groups: [3, 4], length: 7 },
        // Cap-Vert: +238 XXX XXXX (7 chiffres)
        '+238': { groups: [3, 4], length: 7 },
        // Cameroun: +237 X XX XX XX XX (9 chiffres)
        '+237': { groups: [1, 2, 2, 2, 2], length: 9 },
        // Gabon: +241 X XX XX XX (7 chiffres)
        '+241': { groups: [1, 2, 2, 2], length: 7 },
        // Congo: +242 XX XXX XXXX (9 chiffres)
        '+242': { groups: [2, 3, 4], length: 9 },
        // RDC: +243 XXX XXX XXX (9 chiffres)
        '+243': { groups: [3, 3, 3], length: 9 }
      };
      return patterns[indicatif] || { groups: [3, 3, 3], length: 9 }; // Par défaut: XXX XXX XXX
    },

    // Extraire l'indicatif du numéro
    extractIndicatif(phone) {
      if (!phone || !phone.startsWith('+')) return null;

      // Essayer les indicatifs de 4, 3, 2 et 1 chiffres
      const digits = phone.replace(/[^\d+]/g, '');

      // Indicatifs à 4 chiffres (ex: +1242)
      const ind4 = '+' + digits.substring(1, 5);
      if (this.getCountryPattern(ind4) !== this.getCountryPattern('+0')) {
        return ind4;
      }

      // Indicatifs à 3 chiffres (ex: +221, +225)
      const ind3 = '+' + digits.substring(1, 4);
      if (this.getCountryPattern(ind3) !== this.getCountryPattern('+0')) {
        return ind3;
      }

      // Indicatifs à 2 chiffres (ex: +33, +44)
      const ind2 = '+' + digits.substring(1, 3);
      if (this.getCountryPattern(ind2) !== this.getCountryPattern('+0')) {
        return ind2;
      }

      // Indicatif à 1 chiffre (ex: +1)
      const ind1 = '+' + digits.substring(1, 2);
      if (this.getCountryPattern(ind1) !== this.getCountryPattern('+0')) {
        return ind1;
      }

      // Par défaut, prendre les 3 premiers chiffres après le +
      return '+' + digits.substring(1, 4);
    },

    // Formater le numéro selon le pays
    formatPhone(value) {
      if (!value) return '';

      // Ajouter + si absent
      if (!value.startsWith('+')) {
        value = '+' + value;
      }

      // Extraire uniquement les chiffres et le +
      const digitsOnly = value.replace(/[^\d+]/g, '');

      // Extraire l'indicatif
      const indicatif = this.extractIndicatif(digitsOnly);
      if (!indicatif) return value;

      // Extraire le numéro local (sans l'indicatif)
      const localNumber = digitsOnly.substring(indicatif.length);

      // Obtenir le pattern pour ce pays
      const pattern = this.getCountryPattern(indicatif);

      // Formater le numéro local selon le pattern
      let formatted = indicatif;
      let position = 0;

      for (const groupSize of pattern.groups) {
        if (position >= localNumber.length) break;
        const group = localNumber.substring(position, position + groupSize);
        if (group) {
          formatted += ' ' + group;
        }
        position += groupSize;
      }

      // Ajouter les chiffres restants (si le numéro est plus long que prévu)
      if (position < localNumber.length) {
        formatted += ' ' + localNumber.substring(position);
      }

      return formatted;
    },

    onInput(event) {
      let value = event.target.value;

      // Garder la position du curseur
      const cursorPos = event.target.selectionStart;
      const oldLength = value.length;

      // Ajouter + si absent et qu'il y a des chiffres
      if (value && !value.startsWith('+') && /\d/.test(value)) {
        value = '+' + value;
      }

      // Formater
      const formatted = this.formatPhone(value);
      this.displayValue = formatted;

      // Émettre la valeur nettoyée (avec espaces pour lisibilité)
      this.$emit('update:modelValue', formatted.trim());

      // Restaurer la position du curseur de manière intelligente
      this.$nextTick(() => {
        const newLength = this.displayValue.length;
        const diff = newLength - oldLength;
        let newPos = cursorPos + diff;

        // S'assurer que le curseur ne va pas avant l'indicatif
        const indicatif = this.extractIndicatif(this.displayValue);
        const minPos = indicatif ? indicatif.length + 1 : 1;
        newPos = Math.max(minPos, Math.min(newPos, newLength));

        if (this.$refs.input) {
          this.$refs.input.setSelectionRange(newPos, newPos);
        }
      });
    },

    onBlur() {
      // Reformater proprement au blur
      this.displayValue = this.formatPhone(this.displayValue);
      this.$emit('update:modelValue', this.displayValue.trim());
    }
  }
};
</script>

<style scoped>
.phone-input-wrapper {
  width: 100%;
}

.phone-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  letter-spacing: 0.5px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.phone-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.phone-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.phone-input::placeholder {
  color: #9ca3af;
  font-family: inherit;
}
</style>
