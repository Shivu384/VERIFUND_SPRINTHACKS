// Initial rendering of all offers
renderOffers(offersData);
// Modal functionality
const modal = document.getElementById("offerModal");
const addOfferBtn = document.getElementById("addOfferBtn");
const closeModal = document.getElementById("closeModal");
const cancelOffer = document.getElementById("cancelOffer");
const offerForm = document.getElementById("offerForm");

// Show modal
addOfferBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
});

// Close modal
closeModal.addEventListener("click", () => {
    modal.classList.add("hidden");
});

cancelOffer.addEventListener("click", () => {
    modal.classList.add("hidden");
});

// Handle form submission
offerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    
    const newOffer = {
        name: document.getElementById("offerName").value,
        amount: parseInt(document.getElementById("offerAmount").value),
        interest: parseFloat(document.getElementById("offerInterest").value),
        tenor: document.getElementById("offerTenor").value,
        tags: document.getElementById("offerTags").value 
            ? document.getElementById("offerTags").value.split(",").map(tag => tag.trim())
            : []
    };
    
    // Add to beginning of offers array
    offersData.unshift(newOffer);
    
    // Re-render offers
    renderOffers(offersData);
    
    // Reset and close form
    offerForm.reset();
    modal.classList.add("hidden");
});

// Close modal when clicking outside
modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.add("hidden");
    }
});

const offersData = [
    { name: "Axis Bank", amount: 30000, interest: 8, tenor: "3 months", tags: ["Low Interest"] },
    { name: "HDFC Bank", amount: 60000, interest: 10, tenor: "6 months", tags: ["Fast Approval"] },
    { name: "ICICI Bank", amount: 100000, interest: 12, tenor: "1 year", tags: ["Flexible Repayment"] },
    { name: "SBI", amount: 45000, interest: 9.5, tenor: "3 months", tags: ["Low Processing Fee"] },
    { name: "Kotak Mahindra", amount: 75000, interest: 11, tenor: "6 months", tags: ["Easy Application"] },
    { name: "IndusInd Bank", amount: 120000, interest: 10.5, tenor: "1 year", tags: ["Competitive Rates"] },
];

const offersContainer = document.getElementById("offers");
const interestRange = document.getElementById("maxInterest");
const interestDisplay = document.getElementById("interestDisplay");

function renderOffers(offers) {
    offersContainer.innerHTML = ""; // Clear existing offers
    offers.forEach(offer => {
        const offerCard = document.createElement("div");
        offerCard.classList.add("border", "border-gray-300", "rounded-lg", "p-4", "hover:shadow-md", "transition-shadow");
        offerCard.dataset.amount = offer.amount;
        offerCard.dataset.interest = offer.interest;
        offerCard.dataset.tenor = offer.tenor;

        const tagsHtml = offer.tags ? offer.tags.map(tag => `<span class="bg-gray-200 text-green-800 px-2 py-1 rounded-full text-sm">${tag}</span>`).join(' ') : '';

        offerCard.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="font-semibold text-gray-900">${offer.name}</h3>
                    <p class="text-sm text-gray-600">Personal Loan</p>
                </div>
                ${tagsHtml}
            </div>
            <div class="mt-4 grid grid-cols-2 gap-4">
                <div>
                    <p class="text-sm text-gray-600">Amount</p>
                    <p class="font-semibold">₹${offer.amount.toLocaleString()}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Interest Rate</p>
                    <p class="font-semibold text-green-600">${offer.interest}%</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Tenor</p>
                    <p class="font-semibold">${offer.tenor}</p>
                </div>
            </div>
            <button class="mt-4 w-full bg-gray-800 hover:bg-gray-900 text-white px-4 py-2 rounded-lg transition-colors">
                Apply Now
            </button>
        `;
        offersContainer.appendChild(offerCard);
    });
}

interestRange.addEventListener("input", () => {
    interestDisplay.textContent = interestRange.value + "%";
});

document.getElementById("applyFilter").addEventListener("click", () => {
    const minAmount = parseInt(document.getElementById("minAmount").value) || 0;
    const maxInterest = parseFloat(interestRange.value);
    const tenor = document.getElementById("tenor").value;

    const filteredOffers = offersData.filter(offer => {
        const isAmountOk = offer.amount >= minAmount;
        const isInterestOk = offer.interest <= maxInterest;
        const isTenorOk = !tenor || offer.tenor.startsWith(tenor.split(' ')[0]); // Match based on number of months/year
        return isAmountOk && isInterestOk && isTenorOk;
    });

    renderOffers(filteredOffers);
});
function openNegotiationModal(offerId, amount, interest, duration) {
    document.getElementById('negotiationModal').classList.remove('hidden');
    document.getElementById('negotiationOfferId').value = offerId;
    document.getElementById('negAmount').value = amount;
    document.getElementById('negInterest').value = interest;
    document.getElementById('negDuration').value = duration;
}

function closeNegotiationModal() {
    document.getElementById('negotiationModal').classList.add('hidden');
}
