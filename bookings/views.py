from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from web3 import Web3
import json
import os
import traceback

from .models import Booking
from .serializers import BookingSerializer

# Swagger
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes
)

# ----------------------------
# BookingViewSet (GET + POST)
# ----------------------------
@extend_schema(
    tags=["Booking"],
    description="Authenticated user can view or create bookings. Only their own bookings are returned.",

    request=OpenApiExample(
        name="CreateBookingExample",
        value={
            "destination": "Nairobi",
            "start_date": "2025-07-10",
            "end_date": "2025-07-15",
            "status": "pending"
        },
        request_only=True
    ),

    responses={
        200: OpenApiResponse(
            response=BookingSerializer,
            description="Returns list of user's bookings or newly created booking",
            examples=[
                OpenApiExample(
                    name="BookingResponseExample",
                    value={
                        "id": 1,
                        "user": 3,
                        "destination": "Nairobi",
                        "start_date": "2025-07-10",
                        "end_date": "2025-07-15",
                        "status": "pending",
                        "created_at": "2025-06-30T15:00:00Z"
                    },
                    response_only=True
                )
            ]
        )
    }
)
class BookingViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=BookingSerializer,
        responses=BookingSerializer,
        tags=["Booking"],
        description="Create a new booking for the authenticated user."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# ----------------------------
# Mint TrailProof (SoulStamp NFT)
# ----------------------------
@extend_schema(
    tags=["Minting"],
    description="Triggers minting of SoulStamp NFT to authenticated user's wallet address. Requires TrailProof contract and ABI.",
    responses={
        200: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mint_trailproof(request):
    user_wallet = Web3.to_checksum_address(request.user.wallet_address)

    try:
        # 1. Connect to RPC
        w3 = Web3(Web3.HTTPProvider(settings.MINT_RPC_URL))
        if not w3.is_connected():
            return Response({"error": "RPC connection failed"}, status=500)

        # 2. Load and extract ABI from Hardhat artifact
        with open(settings.MINT_ABI_PATH) as abi_file:
            artifact = json.load(abi_file)
            abi = artifact["abi"]

        # 3. Prepare contract and signer
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.MINT_CONTRACT_ADDRESS),
            abi=abi
        )
        private_key = settings.MINT_PRIVATE_KEY
        account = w3.eth.account.from_key(private_key)

        # 4. Prepare the mint arguments
        metadata_uri = "https://amber-legal-guppy-153.mypinata.cloud/ipfs/bafkreicro6ti6ipw62bp6hv2tzqqwbcwjgjgk65jl3xijlqaty2naz24gu"  # Replace with real IPFS or booking metadata later

        # 5. Build the transaction
        nonce = w3.eth.get_transaction_count(account.address)
        txn = contract.functions.mint(user_wallet, metadata_uri).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.to_wei('25', 'gwei')
        })

        # 6. Sign and send
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)


        return Response({
            "status": "Mint successful",
            "tx_hash": tx_hash.hex()
        })

    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Minting failed: {str(e)}"}, status=500)
