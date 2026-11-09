/**
 * seed-categories.js — WalletPro Category Seeder
 *
 * Paste the entire contents of this file into the browser DevTools console
 * while the WalletPro app is open.
 *
 * ✅ Re-run safe — will NOT create duplicates (matches by name, case-insensitive).
 * ✅ Preserves all existing categories and all other app data.
 * ✅ Triggers a save + UI re-render after seeding.
 *
 * Group legend:
 *   "needs"   → essentials (50% bucket in 50/30/20 rule)
 *   "wants"   → lifestyle (30% bucket)
 *   "savings" → savings / investments / transfers (20% bucket)
 */

(function seedCategories() {
  const STORAGE_KEY = 'walletpro_m3_blank_v2';

  // ── Category definitions ─────────────────────────────────────────────────
  // Each entry: [name, group, icon, color]
  // group: 'needs' | 'wants' | 'savings'
  const SEED = [
    // ── Food (Eating Out / Ordered)
    ['Online Food Orders',          'wants',   'delivery_dining',     '#EA580C'],
    ['Dining Out',                  'wants',   'restaurant',          '#F97316'],
    ['Street Food & Quick Bites',   'wants',   'lunch_dining',        '#FB923C'],
    ['Snacks & Beverages',          'wants',   'local_cafe',          '#FDBA74'],
    ['Sweets & Bakery',             'wants',   'cake',                '#F59E0B'],

    // ── Groceries & Home
    ['Groceries & Raw Food',        'needs',   'shopping_basket',     '#16A34A'],
    ['Household Essentials',        'needs',   'cleaning_services',   '#15803D'],
    ['Kitchen & Dining Supplies',   'needs',   'kitchen',             '#14532D'],
    ['Home Furnishing & Decor',     'wants',   'chair',               '#7C3AED'],
    ['Home Appliances',             'needs',   'microwave',           '#6D28D9'],
    ['Home Repairs & Maintenance',  'needs',   'handyman',            '#8B5CF6'],
    ['Domestic Help',               'needs',   'person',              '#A78BFA'],
    ['House Rent',                  'needs',   'home',                '#0284C7'],
    ['Garage Rent',                 'needs',   'garage',              '#0369A1'],

    // ── Shopping
    ['Online Shopping',             'wants',   'shopping_bag',        '#9333EA'],
    ['In-store Shopping',           'wants',   'store',               '#7E22CE'],
    ['Clothing & Apparel',          'wants',   'checkroom',           '#A855F7'],
    ['Tailoring & Alterations',     'wants',   'content_cut',         '#C084FC'],
    ['Footwear',                    'wants',   'steps',               '#D946EF'],
    ['Bags & Accessories',          'wants',   'backpack',            '#E879F9'],
    ['Electronics & Gadgets',       'wants',   'devices',             '#6366F1'],
    ['Personal Care Products',      'needs',   'face_retouching_natural', '#EC4899'],
    ['Eyewear',                     'needs',   'visibility',          '#F43F5E'],

    // ── Vehicle & Transport
    ['Vehicle Fuel',                'needs',   'local_gas_station',   '#2563EB'],
    ['Vehicle Servicing',           'needs',   'build',               '#1D4ED8'],
    ['Vehicle Repairs & Spare Parts','needs',  'car_repair',          '#1E40AF'],
    ['Parking Charges',             'needs',   'local_parking',       '#3B82F6'],
    ['Toll & FASTag',               'needs',   'toll',                '#60A5FA'],
    ['Local Transportation',        'needs',   'directions_bus',      '#93C5FD'],
    ['Outstation Transportation',   'wants',   'train',               '#BFDBFE'],

    // ── Travel
    ['Travel & Accommodation',      'wants',   'flight',              '#0EA5E9'],

    // ── Health & Medical
    ['Medicines',                   'needs',   'medication',          '#DC2626'],
    ['Doctor Consultation',         'needs',   'stethoscope',         '#B91C1C'],
    ['Hospital & Medical Tests',    'needs',   'local_hospital',      '#991B1B'],
    ['Dental & Eye Care',           'needs',   'health_and_safety',   '#EF4444'],
    ['Physiotherapy & Treatment',   'needs',   'self_improvement',    '#F87171'],
    ['Vaccination',                 'needs',   'vaccines',            '#FCA5A5'],

    // ── Personal Grooming
    ['Salon & Haircut',             'wants',   'content_cut',         '#DB2777'],
    ['Beauty & Grooming Services',  'wants',   'spa',                 '#BE185D'],

    // ── Entertainment & Subscriptions
    ['OTT & Digital Subscriptions', 'wants',   'tv',                  '#7C3AED'],
    ['Movies & Events',             'wants',   'movie',               '#6D28D9'],
    ['Outings & Recreation',        'wants',   'park',                '#059669'],
    ['Games & Hobbies',             'wants',   'sports_esports',      '#10B981'],

    // ── Utilities & Bills
    ['Mobile Recharge',             'needs',   'phone_android',       '#0D9488'],
    ['Internet & Broadband',        'needs',   'wifi',                '#0F766E'],
    ['Electricity Bill',            'needs',   'bolt',                '#F59E0B'],
    ['Water & Gas Bills',           'needs',   'water_drop',          '#38BDF8'],
    ['DTH & Cable',                 'needs',   'live_tv',             '#6B7280'],
    ['Other Subscriptions',         'wants',   'subscriptions',       '#8B5CF6'],

    // ── Festivals & Social
    ['Gifts',                       'wants',   'redeem',              '#EC4899'],
    ['Birthday & Anniversary',      'wants',   'celebration',         '#F472B6'],
    ['Puja & Religious Expenses',   'wants',   'temple_hindu',        '#F97316'],
    ['Festivals & Decorations',     'wants',   'festival',            '#FBBF24'],
    ['Social Contributions',        'wants',   'group',               '#34D399'],

    // ── Finance & Banking
    ['Banking & Transaction Charges','needs',  'account_balance',     '#6B7280'],
    ['Tax & Government Payments',   'needs',   'account_balance_wallet','#4B5563'],
    ['Insurance',                   'savings', 'shield',              '#0D9488'],
    ['Loan & EMI Payments',         'savings', 'credit_score',        '#0369A1'],
    ['Cash Withdrawal',             'needs',   'money',               '#78716C'],
    ['Money Transfers',             'savings', 'sync_alt',            '#0891B2'],
    ['Donations & Charity',         'wants',   'volunteer_activism',  '#16A34A'],
    ['Miscellaneous',               'needs',   'more_horiz',          '#94A3B8'],

    // ── Office / Work Expenses
    ['Office Breakfast',            'needs',   'free_breakfast',      '#FBBF24'],
    ['Office Lunch',                'needs',   'lunch_dining',        '#F97316'],
    ['Office Dinner',               'needs',   'dinner_dining',       '#EA580C'],
    ['Office Tea & Snacks',         'needs',   'emoji_food_beverage', '#FDE68A'],
    ['Office Commute',              'needs',   'directions_bus',      '#3B82F6'],
    ['Office Parking',              'needs',   'local_parking',       '#60A5FA'],
    ['Office Expenses',             'needs',   'business_center',     '#64748B'],
  ];

  // ── Load state from localStorage ─────────────────────────────────────────
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    console.error('[Seed] ❌ App state not found in localStorage. Make sure WalletPro is loaded first.');
    return;
  }

  let state;
  try {
    state = JSON.parse(raw);
  } catch (err) {
    console.error('[Seed] ❌ Failed to parse app state:', err);
    return;
  }

  if (!Array.isArray(state.categories)) {
    state.categories = [];
  }

  // ── Seed loop ─────────────────────────────────────────────────────────────
  const existingNames = new Set(
    state.categories.map(c => c.name.toLowerCase().trim())
  );

  let added = 0;
  let skipped = 0;

  SEED.forEach(([name, group, icon, color]) => {
    if (existingNames.has(name.toLowerCase().trim())) {
      console.log(`[Seed] ⏭  Skipped (exists): ${name}`);
      skipped++;
      return;
    }

    state.categories.push({
      id:    `cat_seed_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      name,
      type:  'expense',
      group, // 'needs' | 'wants' | 'savings'
      icon,
      color,
    });

    existingNames.add(name.toLowerCase().trim()); // prevent duplicate within same seed run
    added++;
    console.log(`[Seed] ✅ Added [${group.toUpperCase()}]: ${name}`);
  });

  // ── Save & refresh UI ─────────────────────────────────────────────────────
  state.updatedAt = Date.now();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));

  // Trigger live UI refresh if the app is running
  if (typeof renderAll === 'function') {
    // Update in-memory state so renderAll reflects changes immediately
    if (typeof state !== 'undefined' && window.state !== undefined) {
      window.state = state;
    }
    renderAll();
    console.log('[Seed] 🎨 UI refreshed via renderAll()');
  } else {
    console.warn('[Seed] ⚠️  renderAll() not found — please refresh the page to see changes.');
  }

  console.log(`\n[Seed] ✅ Done! Added: ${added} | Skipped (duplicates): ${skipped} | Total categories: ${state.categories.length}`);
})();

